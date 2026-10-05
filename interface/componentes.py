# interface/componentes.py

import customtkinter as ctk

from interface.tema import CORES

# ============================================================
# CARD
# ============================================================


class CardIndicador(ctk.CTkFrame):

    def __init__(self, master, titulo, valor="0", icone="", **kwargs):

        super().__init__(
            master,
            fg_color=CORES["card"],
            corner_radius=12,
            border_width=1,
            border_color=CORES["borda"],
            **kwargs
        )

        # ----------------------------------------------------
        # ÍCONE
        # ----------------------------------------------------

        self.label_icone = ctk.CTkLabel(self, text=icone, font=ctk.CTkFont(size=22))

        self.label_icone.pack(anchor="w", padx=18, pady=(15, 0))

        # ----------------------------------------------------
        # TÍTULO
        # ----------------------------------------------------

        self.label_titulo = ctk.CTkLabel(
            self,
            text=titulo,
            text_color=CORES["texto_secundario"],
            font=ctk.CTkFont(size=13),
        )

        self.label_titulo.pack(anchor="w", padx=18, pady=(8, 0))

        # ----------------------------------------------------
        # VALOR
        # ----------------------------------------------------

        self.label_valor = ctk.CTkLabel(
            self,
            text=str(valor),
            text_color=CORES["texto"],
            font=ctk.CTkFont(size=25, weight="bold"),
        )

        self.label_valor.pack(anchor="w", padx=18, pady=(2, 15))

    def atualizar(self, valor):

        self.label_valor.configure(text=str(valor))


# ============================================================
# BOTÃO PRINCIPAL
# ============================================================


class BotaoPrincipal(ctk.CTkButton):

    def __init__(self, master, text, command=None, **kwargs):

        super().__init__(
            master,
            text=text,
            command=command,
            fg_color=CORES["destaque"],
            hover_color=CORES["destaque_hover"],
            text_color="#FFFFFF",
            corner_radius=8,
            height=38,
            **kwargs
        )


# ============================================================
# TÍTULO DE SEÇÃO
# ============================================================


class TituloSecao(ctk.CTkLabel):

    def __init__(self, master, text, **kwargs):

        super().__init__(
            master,
            text=text,
            text_color=CORES["texto"],
            font=ctk.CTkFont(size=20, weight="bold"),
            **kwargs
        )


# ============================================================
# MENSAGEM
# ============================================================


class Mensagem(ctk.CTkLabel):

    def __init__(self, master, text, tipo="normal", **kwargs):

        cores = {
            "normal": CORES["texto_secundario"],
            "sucesso": CORES["sucesso"],
            "erro": CORES["erro"],
            "alerta": CORES["alerta"],
        }

        super().__init__(
            master,
            text=text,
            text_color=cores.get(tipo, CORES["texto_secundario"]),
            font=ctk.CTkFont(size=13),
            **kwargs
        )
