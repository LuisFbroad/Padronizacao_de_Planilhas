import pandas as pd


class PadronizadorExcel:
    """Responsável por padronizar os dados das planilhas."""

    MAPA_COLUNAS = {
        "Qnt.": "quantidade",
        "Quantidade": "quantidade",

        "Data": "data",
        "DATA": "data",

        "Semana": "semana",
        "SEMANA": "semana",

        "Cliente": "cliente",
        "CLIENTE": "cliente",

        "CPF": "cpf",

        "Valor": "valor",
        "VALOR": "valor",

        "INDICAÇÃO PRIMÁRIA": "indicacao_primaria",
        "INDICAÇÃO SECUNDÁRIA": "indicacao_secundaria",
        "INDICAÇÃO TERCIÁRIA": "indicacao_terciaria",
        "INDICAÇÃO QUARTERNARIA": "indicacao_quaternaria",
        "INDICAÇÃO FINAL": "indicacao_final",

        "Honorários": "honorarios",

        "Nº do Processo": "numero_processo",
        "NÚMERO DO PROCESSO": "numero_processo",

        "PRC/RPV": "prc_rpv",

        "Valor Mensurado": "valor_mensurado",
        "VALOR MENSURADO": "valor_mensurado",

        "Assunto": "assunto",
        "ASSUNTO": "assunto",
    }

    def padronizar_colunas(
        self,
        dados: pd.DataFrame
    ) -> pd.DataFrame:

        dados = dados.copy()

        dados = dados.rename(
            columns=self.MAPA_COLUNAS
        )

        return dados

    def padronizar(
        self,
        dados: pd.DataFrame
    ) -> pd.DataFrame:

        dados = self.padronizar_colunas(dados)

        return dados