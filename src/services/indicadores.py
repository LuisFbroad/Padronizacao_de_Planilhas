from pathlib import Path

import pandas as pd

from src.database.connection import SessionLocal
from src.database.models import Pessoa, Area, Indicacao

PASTA_DADOS = Path("__Agosto_Padrão__")

COLUNAS_INDICACAO = [
    "INDICAÇÃO PRIMÁRIA",
    "INDICAÇÃO SECUNDÁRIA",
    "INDICAÇÃO TERCIÁRIA",
    "INDICAÇÃO QUARTERNARIA",
    "INDICAÇÃO FINAL",
]


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
        raise ValueError(f"Área '{nome_area}' não encontrada no banco de dados.")

    return area


def importar_planilha(caminho, session):
    nome_arquivo = caminho.name

    area_nome = identificar_area(nome_arquivo)

    if not area_nome:
        print(f"[AVISO] Área não identificada: {nome_arquivo}")
        return 0

    print()
    print("=" * 80)
    print(f"IMPORTANDO: {nome_arquivo}")
    print(f"Área: {area_nome}")
    print("=" * 80)

    df = pd.read_excel(caminho, header=3)

    area = buscar_area(session, area_nome)

    total_processos = 0
    total_indicacoes = 0

    for indice, linha in df.iterrows():

        processo = limpar_valor(linha.get("Nº do Processo"))

        data_indicacao = linha.get("Data")

        if pd.notna(data_indicacao):
            try:
                data_indicacao = pd.to_datetime(data_indicacao).date()
            except Exception:
                data_indicacao = None
        else:
            data_indicacao = None

        indicadores_do_processo = set()

        for coluna in COLUNAS_INDICACAO:

            if coluna not in df.columns:
                continue

            valor = limpar_valor(linha.get(coluna))

            if valor is None:
                continue

            indicadores_do_processo.add(valor)

        if not indicadores_do_processo:
            continue

        total_processos += 1

        for nome_indicador in indicadores_do_processo:

            pessoa = buscar_ou_criar_pessoa(session, nome_indicador)

            existe = (
                session.query(Indicacao)
                .filter(
                    Indicacao.pessoa_id == pessoa.id,
                    Indicacao.area_id == area.id,
                    Indicacao.processo == processo,
                )
                .first()
            )

            if existe:
                continue

            indicacao = Indicacao(
                pessoa_id=pessoa.id,
                area_id=area.id,
                processo=processo,
                arquivo_origem=nome_arquivo,
                data_indicacao=data_indicacao,
            )

            session.add(indicacao)

            total_indicacoes += 1

    print(f"Processos encontrados: {total_processos}")
    print(f"Indicações inseridas: {total_indicacoes}")

    return total_indicacoes


def importar_todas():
    arquivos = sorted(PASTA_DADOS.glob("*.xlsx"))

    if not arquivos:
        print("Nenhuma planilha encontrada.")
        return

    session = SessionLocal()

    total_geral = 0

    try:

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
