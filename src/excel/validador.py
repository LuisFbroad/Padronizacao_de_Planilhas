import pandas as pd


class ValidadorExcel:
    """Responsável por verificar se os dados da planilha estão corretos."""

    CAMPOS_OBRIGATORIOS = [
        "cliente",
        "data",
    ]

    def validar_colunas(self, dados: pd.DataFrame) -> list[str]:
        """
        Verifica se as colunas obrigatórias existem na planilha.
        """

        erros = []

        for coluna in self.CAMPOS_OBRIGATORIOS:
            if coluna not in dados.columns:
                erros.append(f"Coluna obrigatória ausente: {coluna}")

        return erros

    def validar_dados(self, dados: pd.DataFrame) -> list[str]:
        """
        Verifica se existem dados faltando nos campos obrigatórios.
        """

        erros = []

        for coluna in self.CAMPOS_OBRIGATORIOS:

            if coluna not in dados.columns:
                continue

            vazios = dados[coluna].isna().sum()

            if vazios > 0:
                erros.append(
                    f"A coluna '{coluna}' possui " f"{vazios} registro(s) vazio(s)."
                )

        return erros

    def validar(self, dados: pd.DataFrame) -> list[str]:
        """
        Executa todas as validações.
        """

        erros = []

        erros.extend(self.validar_colunas(dados))

        erros.extend(self.validar_dados(dados))

        return erros
