import customtkinter as ctk

CORES = {
    # Fundo principal
    "fundo": "#0B1736",
    "fundo_secundario": "#101F45",
    # Menu lateral
    "sidebar": "#071126",
    "sidebar_hover": "#162754",
    # Cards
    "card": "#14244A",
    "card_hover": "#1A2D59",
    # Textos
    "texto": "#FFFFFF",
    "texto_secundario": "#B8C2D6",
    "texto_claro": "#FFFFFF",
    # Identidade GAGC
    "destaque": "#B08D3C",
    "destaque_hover": "#96762F",
    # Status
    "sucesso": "#4CAF50",
    "erro": "#EF5350",
    "alerta": "#F9A825",
    # Bordas
    "borda": "#263A64",
}


def configurar_tema():
    """
    Configura o tema fixo do sistema.
    O sistema utiliza apenas o tema azul-marinho.
    """

    ctk.set_appearance_mode("dark")
    ctk.set_default_color_theme("blue")
