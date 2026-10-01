from src.excel.leitor import LeitorExcel


CAMINHO_EXCEL = "data/entrada/RELATORIO MENSAL PADRÃO.xlsx"


def main():
    leitor = LeitorExcel(CAMINHO_EXCEL)

    print("\nABAS ENCONTRADAS:")

    for aba in leitor.listar_abas():
        print(f"- {aba}")

    print("\nLENDO RELATÓRIO MENSAL...")

    dados = leitor.ler_aba("RELATÓRIO MENSAL (NOVOS)")

    print(f"\nLinhas encontradas: {len(dados)}")
    print(f"Colunas encontradas: {len(dados.columns)}")

    print("\nCOLUNAS:")

    for coluna in dados.columns:
        print(f"- {coluna}")

    print("\nPRIMEIROS REGISTROS:")
    print(dados.head())


if __name__ == "__main__":
    main()