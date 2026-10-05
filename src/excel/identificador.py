import pandas as pd

from src.excel.tipos_planilha import TipoPlanilha


class IdentificadorPlanilha:
    """
    Identifica automaticamente qual é o tipo da planilha.
    """

    REGRAS = {
        TipoPlanilha.CIV: {
            "cliente",
            "data",
            "indicacoes",
        },
        TipoPlanilha.PREV: {
            "nº",
            "data",
            "cliente",
            "cpf",
            "indicacoes",
        },
        TipoPlanilha.PROJ: {
            "data",
            "semana",
            "tipo",
            "servidor",
            "sucessores",
            "valor",
            "honorários (%)",
            "valor dos honorários",
            "prc/rpv",
        },
        TipoPlanilha.REV: {
            "quantidade",
            "data",
            "uf",
            "competência",
            "indicação",
            "cliente",
            "cpf",
            "número do processo",
            "valor mensurado",
            "%",
            "honorários",
            "assunto",
        },
        TipoPlanilha.TRAB: {
            "nº",
            "data",
            "cliente",
            "indicações",
        },
    }

    def identificar(self, dados: pd.DataFrame) -> TipoPlanilha:

        colunas = {str(coluna).strip().lower() for coluna in dados.columns}

        melhor_tipo = TipoPlanilha.DESCONHECIDA
        maior_pontuacao = 0

        for tipo, regras in self.REGRAS.items():

            pontuacao = len(colunas.intersection(regras))

            if pontuacao > maior_pontuacao:
                maior_pontuacao = pontuacao
                melhor_tipo = tipo

        return melhor_tipo
