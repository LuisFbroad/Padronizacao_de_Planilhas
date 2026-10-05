from pathlib import Path

import pandas as pd


class LeitorExcel:
    """Responsável por carregar e consultar arquivos Excel."""

    def __init__(self, caminho: str | Path):

        self.caminho = Path(caminho)

        if not self.caminho.exists():
            raise FileNotFoundError(f"Arquivo não encontrado: {self.caminho}")

        if self.caminho.suffix.lower() not in [".xlsx", ".xlsm", ".xls"]:
            raise ValueError("O arquivo informado não é um Excel válido.")

    # ==========================================================
    # LISTAR ABAS
    # ==========================================================

    def listar_abas(self) -> list[str]:
        """Retorna o nome de todas as abas do arquivo."""

        arquivo = pd.ExcelFile(self.caminho)

        return arquivo.sheet_names

    # ==========================================================
    # LER UMA ABA
    # ==========================================================

    def ler_aba(self, nome_aba: str, linha_cabecalho: int = 3) -> pd.DataFrame:
        """
        Lê uma aba específica do Excel.

        linha_cabecalho:
            Número da linha onde estão os nomes das colunas.
            No Excel, a linha 4 corresponde ao índice 3
            no pandas.
        """

        abas = self.listar_abas()

        if nome_aba not in abas:
            raise ValueError(f"A aba '{nome_aba}' não existe no arquivo.")

        dados = pd.read_excel(self.caminho, sheet_name=nome_aba, header=linha_cabecalho)

        return dados

    # ==========================================================
    # LER TODAS AS ABAS
    # ==========================================================

    def ler_todas_abas(self) -> dict[str, pd.DataFrame]:
        """Lê todas as abas do arquivo."""

        return pd.read_excel(self.caminho, sheet_name=None)
