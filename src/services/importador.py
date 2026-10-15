from pathlib import Path
import unicodedata

import pandas as pd

from src.database.connection import SessionLocal
from src.database.models import Pessoa, Area, Indicacao

PASTA_DADOS = Path("__Agosto_Padrão__")


COLUNAS_INDICACAO = {
    "INDICACAO PRIMARIA": "Primária",
    "INDICACAO SECUNDARIA": "Secundária",
    "INDICACAO TERCIARIA": "Terciária",
    "INDICACAO QUARTERNARIA": "Quaternária",
    "INDICACAO QUATERNARIA": "Quaternária",
    "INDICACAO FINAL": "Final",
}


AREAS = {
    "CIV": "Cível",
    "PREV": "Previdenciário",
    "PROJ": "Projetos",
    "REV": "Revisão",
    "TRAB": "Trabalhista",
}


def normalizar_texto(valor):
    texto = str(valor).strip().upper()
    texto = unicodedata.normalize("NFKD", texto)

    return "".join(
        caractere for caractere in texto if not unicodedata.combining(caractere)
    )


def limpar_valor(valor):
    if pd.isna(valor):
        return None

    valor = str(valor).strip()

    if not valor or valor.lower() == "nan":
        return None

    return valor


def identificar_area(nome_arquivo):
    nome = normalizar_texto(nome_arquivo)

    for sigla, area in AREAS.items():
        if f"_{sigla}_" in nome:
            return area

    return None


def buscar_ou_criar_pessoa(session, nome):
    pessoa = session.query(Pessoa).filter(Pessoa.nome == nome).first()

    if pessoa:
        return pessoa

    pessoa = Pessoa(nome=nome)
    session.add(pessoa)
    session.flush()

    return pessoa


def buscar_area(session, nome_area):
    area = session.query(Area).filter(Area.nome == nome_area).first()

    if not area:
        raise ValueError(f"Área '{nome_area}' não encontrada no banco.")

    return area


def obter_colunas_normalizadas(df):
    mapa = {}

    for coluna in df.columns:
        mapa[normalizar_texto(coluna)] = coluna

    return mapa


def obter_valor_coluna(linha, mapa_colunas, nome_coluna):
    chave = normalizar_texto(nome_coluna)
    coluna_real = mapa_colunas.get(chave)

    if coluna_real is None:
        return None

    return linha.get(coluna_real)


def obter_processo(linha, mapa_colunas):
    processo = limpar_valor(
        obter_valor_coluna(
            linha,
            mapa_colunas,
            "Nº do Processo",
        )
    )

    if processo:
        return processo

    return limpar_valor(
        obter_valor_coluna(
            linha,
            mapa_colunas,
            "PRC/RPV",
        )
    )


def obter_data_indicacao(linha, mapa_colunas):
    valor = obter_valor_coluna(
        linha,
        mapa_colunas,
        "Data",
    )

    if valor is None or pd.isna(valor):
        return None

    data = pd.to_datetime(
        valor,
        errors="coerce",
        dayfirst=True,
    )

    if pd.isna(data):
        return None

    return data.date()


def obter_indicacoes(linha, mapa_colunas):
    indicacoes = []

    for coluna_normalizada, tipo in COLUNAS_INDICACAO.items():
        coluna_real = mapa_colunas.get(coluna_normalizada)

        if coluna_real is None:
            continue

        valor = limpar_valor(linha.get(coluna_real))

        if not valor:
            continue

        for parte in valor.split("/"):
            nome = parte.strip()

            if nome:
                indicacoes.append(
                    {
                        "nome": nome,
                        "tipo": tipo,
                    }
                )

    return indicacoes


def importar_planilha(caminho, session):
    nome_arquivo = caminho.name
    area_nome = identificar_area(nome_arquivo)

    if not area_nome:
        print(f"[AVISO] Área não identificada: {nome_arquivo}")
        return 0

    print()
    print("=" * 80)
    print(f"ARQUIVO: {nome_arquivo}")
    print(f"ÁREA: {area_nome}")
    print("=" * 80)

    df = pd.read_excel(caminho, header=3)

    mapa_colunas = obter_colunas_normalizadas(df)
    area = buscar_area(session, area_nome)

    total_processos = 0
    total_indicacoes = 0

    # Evita processar a mesma indicação duas vezes
    # durante a importação das planilhas atuais.
    indicacoes_processadas = set()

    for _, linha in df.iterrows():
        processo = obter_processo(linha, mapa_colunas)
        data_indicacao = obter_data_indicacao(
            linha,
            mapa_colunas,
        )
        indicacoes = obter_indicacoes(
            linha,
            mapa_colunas,
        )

        if not processo or not indicacoes:
            continue

        total_processos += 1

        for indicacao_data in indicacoes:
            nome = indicacao_data["nome"]
            tipo = indicacao_data["tipo"]

            pessoa = buscar_ou_criar_pessoa(
                session,
                nome,
            )

            # A data não faz parte da chave.
            chave = (
                pessoa.id,
                area.id,
                processo,
                tipo,
            )

            if chave in indicacoes_processadas:
                continue

            # Procura uma indicação existente no banco,
            # independentemente da data registrada.
            consulta = (
                session.query(Indicacao)
                .filter(
                    Indicacao.pessoa_id == pessoa.id,
                    Indicacao.area_id == area.id,
                    Indicacao.processo == processo,
                    Indicacao.tipo_indicacao == tipo,
                )
                .first()
            )

            if consulta:
                # Atualiza a data somente se a planilha
                # apresentar uma data válida.
                if data_indicacao is not None:
                    consulta.data_indicacao = data_indicacao

                indicacoes_processadas.add(chave)
                continue

            # Cria somente indicações que ainda não existem.
            indicacao = Indicacao(
                pessoa_id=pessoa.id,
                area_id=area.id,
                processo=processo,
                tipo_indicacao=tipo,
                data_indicacao=data_indicacao,
                arquivo_origem=nome_arquivo,
            )

            session.add(indicacao)
            indicacoes_processadas.add(chave)
            total_indicacoes += 1

    print(f"Processos com indicação: {total_processos}")
    print(f"Indicações inseridas: {total_indicacoes}")

    return total_indicacoes


def importar_todas():
    if not PASTA_DADOS.exists():
        print(f"Pasta não encontrada: {PASTA_DADOS}")
        return

    arquivos = sorted(PASTA_DADOS.glob("*.xlsx"))

    if not arquivos:
        print("Nenhuma planilha encontrada.")
        return

    session = SessionLocal()
    total_geral = 0

    try:
        print("=" * 80)
        print("IMPORTAÇÃO DAS PLANILHAS")
        print("=" * 80)
        print(f"Planilhas encontradas: {len(arquivos)}")

        for arquivo in arquivos:
            total_geral += importar_planilha(
                arquivo,
                session,
            )

        session.commit()

        print()
        print("=" * 80)
        print("IMPORTAÇÃO CONCLUÍDA")
        print("=" * 80)
        print(f"Total de indicações inseridas: {total_geral}")

    except Exception as erro:
        session.rollback()

        print("ERRO DURANTE A IMPORTAÇÃO")
        print(erro)

        raise

    finally:
        session.close()


if __name__ == "__main__":
    importar_todas()
