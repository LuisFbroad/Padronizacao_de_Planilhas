import customtkinter as ctk


CORES = {
    # Fundos
    "fundo": "#0B1736",
    "fundo_secundario": "#101F45",

    # Menu lateral
    "sidebar": "#071126",
    "sidebar_hover": "#162754",
    "sidebar_selecionado": "#1A2D59",

    # Cards
    "card": "#14244A",
    "card_hover": "#1A2D59",

    # Textos
    "texto": "#FFFFFF",
    "texto_claro": "#FFFFFF",
    "texto_secundario": "#B8C2D6",
    "texto_botao": "#071126",
    "texto_desativado": "#74819A",

    # Identidade GAGC
    "destaque": "#B08D3C",
    "destaque_hover": "#96762F",
    "destaque_claro": "#D1B56B",

    # Status
    "sucesso": "#4CAF50",
    "erro": "#EF5350",
    "alerta": "#F9A825",

    # Bordas
    "borda": "#263A64",
    "borda_destaque": "#B08D3C",

    # Campos de entrada
    "campo": "#0D1B3A",
    "campo_borda": "#304571",

    # Tabelas e listas
    "linha_alternada": "#101F45",
    "linha_selecionada": "#1A2D59",
}


def configurar_tema():
    """
    Configura o tema visual fixo do Sistema GAGC.
    """

    ctk.set_appearance_mode("dark")
    ctk.set_default_color_theme("blue")