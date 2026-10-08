from pathlib import Path

import pandas as pd

from src.database.connection import SessionLocal
from src.database.models import Pessoa, Area, Indicacao

PASTA_DADOS = Path("__Agosto_Padrão__")


COLUNAS_INDICACAO = {
    "INDICAÇÃO PRIMÁRIA": "Primária",
    "INDICAÇÃO SECUNDÁRIA": "Secundária",
    "INDICAÇÃO TERCIÁRIA": "Terciária",
    "INDICAÇÃO QUARTERNARIA": "Quaternária",
    "INDICAÇÃO FINAL": "Final",
}


AREAS = {
    "CIV": "Cível",
    "PREV": "Previdenciário",
    "PROJ": "Projetos",
    "REV": "Revisão",
    "TRAB": "Trabalhista",
}


def identificar_area(nome_arquivo):
    nome = nome_arquivo.upper()

    for sigla, area in AREAS.items():
        if f"_{sigla}_" in nome:
            return area

    return None


def limpar_valor(valor):
    if pd.isna(valor):
        return None

    valor = str(valor).strip()

    if not valor:
        return None

    return valor


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


def obter_processo(linha):
    processo = limpar_valor(linha.get("Nº do Processo"))

    if processo:
        return processo

    processo = limpar_valor(linha.get("PRC/RPV"))

    if processo:
        return processo

    return None


def obter_indicacoes(linha):
    indicacoes = []

    for coluna, tipo in COLUNAS_INDICACAO.items():

        if coluna not in linha.index:
            continue

        valor = limpar_valor(linha[coluna])

        if not valor:
            continue

        partes = valor.split("/")

        for parte in partes:

            pessoa = parte.strip()

            if pessoa:
                indicacoes.append(
                    {
                        "nome": pessoa,
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

    area = buscar_area(session, area_nome)

    total_processos = 0
    total_indicacoes = 0

    # Guarda as indicações que já foram processadas
    # durante esta própria planilha.
    indicacoes_processadas = set()

    for indice, linha in df.iterrows():

        processo = obter_processo(linha)

        indicacoes = obter_indicacoes(linha)

        # Não importa registros sem processo
        # ou sem indicação.
        if not processo or not indicacoes:
            continue

        total_processos += 1

        for indicacao_data in indicacoes:

            nome = indicacao_data["nome"]
            tipo = indicacao_data["tipo"]

            pessoa = buscar_ou_criar_pessoa(session, nome)

            # Chave completa da indicação.
            #
            # Assim podemos identificar duplicações
            # que aparecem duas vezes na própria planilha.
            chave = (
                pessoa.id,
                area.id,
                processo,
                tipo,
            )

            # Se essa indicação já apareceu anteriormente
            # nesta mesma planilha, ignora.
            if chave in indicacoes_processadas:
                continue

            # Verifica se já existe no banco.
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
                continue

            indicacao = Indicacao(
                pessoa_id=pessoa.id,
                area_id=area.id,
                processo=processo,
                tipo_indicacao=tipo,
                arquivo_origem=nome_arquivo,
            )

            session.add(indicacao)

            # Marca como processada.
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

            total = importar_planilha(arquivo, session)

            total_geral += total

        session.commit()

        print()
        print("=" * 80)
        print("IMPORTAÇÃO CONCLUÍDA")
        print("=" * 80)

        print(f"Total de indicações inseridas: {total_geral}")

    except Exception as erro:

        session.rollback()

        print()
        print("=" * 80)
        print("ERRO DURANTE A IMPORTAÇÃO")
        print("=" * 80)

        print(erro)

        raise

    finally:

        session.close()


if __name__ == "__main__":
    importar_todas()
