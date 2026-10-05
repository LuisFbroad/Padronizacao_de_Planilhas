import pandas as pd


class IndicadoresService:
    """
    Responsável por calcular indicadores a partir
    dos dados carregados da planilha.
    """

    # ==========================================
    # COLUNAS DE INDICAÇÃO DISPONÍVEIS
    # ==========================================

    COLUNAS_INDICACAO = {
        "Primária": "indicacao_primaria",
        "Secundária": "indicacao_secundaria",
        "Terciária": "indicacao_terciaria",
        "Quaternária": "indicacao_quaternaria",
        "Final": "indicacao_final",
    }

    def __init__(self, dados: pd.DataFrame):
        """
        Recebe o DataFrame já carregado e padronizado.
        """

        self.dados = dados.copy()

    # ==========================================
    # VERIFICAR COLUNA
    # ==========================================

    def verificar_coluna(self, coluna: str) -> bool:
        """
        Verifica se determinada coluna existe na planilha.
        """

        return coluna in self.dados.columns

    # ==========================================
    # CONTAR INDICAÇÕES
    # ==========================================

    def contar_indicacoes(self, tipo: str = "Primária") -> pd.DataFrame:
        """
        Conta quantas pessoas cada indicador indicou.

        Exemplo:

        LUIS FELIPE -> 5
        JOÃO        -> 3
        MARIA       -> 2
        """

        # --------------------------------------
        # Verifica se o tipo existe
        # --------------------------------------

        if tipo not in self.COLUNAS_INDICACAO:
            raise ValueError(f"Tipo de indicação inválido: {tipo}")

        coluna = self.COLUNAS_INDICACAO[tipo]

        # --------------------------------------
        # Verifica se a coluna existe
        # --------------------------------------

        if not self.verificar_coluna(coluna):

            raise ValueError(f"A coluna '{coluna}' não existe " "na planilha.")

        # --------------------------------------
        # Seleciona a coluna
        # --------------------------------------

        indicacoes = self.dados[coluna]

        # --------------------------------------
        # Remove valores vazios
        # --------------------------------------

        indicacoes = indicacoes.dropna()

        # --------------------------------------
        # Remove textos vazios
        # --------------------------------------

        indicacoes = indicacoes[indicacoes.astype(str).str.strip() != ""]

        # --------------------------------------
        # Conta as ocorrências
        # --------------------------------------

        resultado = indicacoes.astype(str).str.strip().value_counts().reset_index()

        # --------------------------------------
        # Renomeia as colunas
        # --------------------------------------

        resultado.columns = ["indicador", "quantidade"]

        # --------------------------------------
        # Ordena do maior para o menor
        # --------------------------------------

        resultado = resultado.sort_values(by="quantidade", ascending=False)

        # --------------------------------------
        # Reseta o índice
        # --------------------------------------

        resultado = resultado.reset_index(drop=True)

        return resultado

    # ==========================================
    # PESQUISAR UM INDICADOR
    # ==========================================

    def pesquisar_indicador(self, nome: str, tipo: str = "Primária") -> int:
        """
        Retorna quantas pessoas foram indicadas
        por um determinado indicador.

        Exemplo:

        pesquisar_indicador("LUIS FELIPE")

        Retorno:

        5
        """

        resultado = self.contar_indicacoes(tipo)

        nome_pesquisa = str(nome).strip().upper()

        resultado["indicador_normalizado"] = (
            resultado["indicador"].astype(str).str.strip().str.upper()
        )

        encontrado = resultado[resultado["indicador_normalizado"] == nome_pesquisa]

        if encontrado.empty:
            return 0

        return int(encontrado.iloc[0]["quantidade"])

    # ==========================================
    # TOTAL DE INDICAÇÕES
    # ==========================================

    def total_indicacoes(self, tipo: str = "Primária") -> int:
        """
        Retorna o número total de indicações.
        """

        resultado = self.contar_indicacoes(tipo)

        return int(resultado["quantidade"].sum())

    # ==========================================
    # QUANTIDADE DE INDICADORES
    # ==========================================

    def quantidade_indicadores(self, tipo: str = "Primária") -> int:
        """
        Retorna quantos indicadores diferentes
        existem na planilha.
        """

        resultado = self.contar_indicacoes(tipo)

        return len(resultado)

    def contar_todas_indicacoes(self) -> pd.DataFrame:
        """
        Conta todas as indicações existentes,
        independentemente do tipo.
        """

        colunas = [
            "indicacao_primaria",
            "indicacao_secundaria",
            "indicacao_terciaria",
            "indicacao_quaternaria",
            "indicacao_final",
        ]

        series = []

        for coluna in colunas:

            if coluna not in self.dados.columns:
                continue

            indicacoes = self.dados[coluna]

            indicacoes = indicacoes.dropna()

            indicacoes = indicacoes[
                indicacoes.astype(str).str.strip() != ""
            ]

            if not indicacoes.empty:
                series.append(
                    indicacoes.astype(str).str.strip()
                )

        if not series:

            return pd.DataFrame(
                columns=[
                    "indicador",
                    "quantidade"
                ]
            )

        todas = pd.concat(
            series,
            ignore_index=True
        )

        resultado = (
            todas
            .value_counts()
            .reset_index()
        )

        resultado.columns = [
            "indicador",
            "quantidade"
        ]

        resultado = resultado.sort_values(
            by="quantidade",
            ascending=False
        )

        resultado = resultado.reset_index(
            drop=True
        )

        return resultado