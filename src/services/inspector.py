import pandas as pd
from pathlib import Path


PASTA_DADOS = Path("__Agosto_Padrão__")

COLUNAS_INDICACAO = [
    "INDICAÇÃO PRIMÁRIA",
    "INDICAÇÃO SECUNDÁRIA",
    "INDICAÇÃO TERCIÁRIA",
    "INDICAÇÃO QUARTERNARIA",
    "INDICAÇÃO FINAL",
]


def identificar_area(nome_arquivo):
    nome = nome_arquivo.upper()

    if "_CIV_" in nome:
        return "Cível"

    if "_PREV_" in nome:
        return "Previdenciário"

    if "_PROJ_" in nome:
        return "Projetos"

    if "_REV_" in nome:
        return "Revisão"

    if "_TRAB_" in nome:
        return "Trabalhista"

    return "Desconhecida"


def limpar_valor(valor):
    if pd.isna(valor):
        return ""

    valor = str(valor).strip()

    if valor in ["", "-", "nan", "NaN"]:
        return ""

    return valor


def mostrar_campo(nome, valor):
    valor = limpar_valor(valor)

    if valor:
        print(f"{nome}: {valor}")
    else:
        print(f"{nome}: -")


def analisar_planilha(caminho):
    print("\n" + "=" * 100)
    print(f"ARQUIVO: {caminho.name}")
    print("=" * 100)

    area = identificar_area(caminho.name)

    print(f"Área identificada: {area}")

    try:
        df = pd.read_excel(caminho, header=3)
    except Exception as erro:
        print(f"ERRO AO LER PLANILHA: {erro}")
        return

    print(f"Linhas de dados: {len(df)}")
    print(f"Colunas: {len(df.columns)}")

    colunas_importantes = [
        "Qnt.",
        "Data",
        "Semana",
        "Cliente",
        "CPF",
        "Valor",
        "INDICAÇÃO PRIMÁRIA",
        "INDICAÇÃO SECUNDÁRIA",
        "INDICAÇÃO TERCIÁRIA",
        "INDICAÇÃO QUARTERNARIA",
        "INDICAÇÃO FINAL",
        "Honorários",
        "Nº do Processo",
        "PRC/RPV",
        "Valor Mensurado",
        "Assunto",
    ]

    colunas_existentes = [
        coluna
        for coluna in colunas_importantes
        if coluna in df.columns
    ]

    for indice, linha in df.iterrows():

        print("\n" + "-" * 100)
        print(f"Linha do Excel: {indice + 5}")
        print("-" * 100)

        for coluna in colunas_existentes:

            valor = linha[coluna]

            if limpar_valor(valor):
                mostrar_campo(coluna, valor)

    print("\n" + "=" * 100)
    print(f"FIM DO ARQUIVO: {caminho.name}")
    print("=" * 100)


def executar():
    if not PASTA_DADOS.exists():
        print(f"Pasta não encontrada: {PASTA_DADOS}")
        return

    arquivos = sorted(PASTA_DADOS.glob("*.xlsx"))

    if not arquivos:
        print(f"Nenhuma planilha encontrada em: {PASTA_DADOS}")
        return

    print("=" * 100)
    print("INSPEÇÃO DETALHADA DAS PLANILHAS")
    print("=" * 100)

    print(f"\nPasta analisada: {PASTA_DADOS}")
    print(f"Planilhas encontradas: {len(arquivos)}")

    for arquivo in arquivos:
        analisar_planilha(arquivo)

    print("\n" + "=" * 100)
    print("FIM DA INSPEÇÃO")
    print("=" * 100)


if __name__ == "__main__":
    executar()