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

    def listar_abas(self) -> list[str]:
        """Retorna o nome de todas as abas do arquivo."""
        arquivo = pd.ExcelFile(self.caminho)
        return arquivo.sheet_names

    def ler_aba(self, nome_aba: str) -> pd.DataFrame:
        """Lê uma aba do Excel usando a linha 4 como cabeçalho."""

        return pd.read_excel(self.caminho, sheet_name=nome_aba, header=3)

    def ler_todas_abas(self) -> dict[str, pd.DataFrame]:
        """Lê todas as abas do Excel."""
        return pd.read_excel(self.caminho, sheet_name=None)
