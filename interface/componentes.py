import customtkinter as ctk

from interface.tema import CORES


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

        self.grid_columnconfigure(1, weight=1)

        self.icone_label = ctk.CTkLabel(
            self,
            text=icone,
            text_color=CORES["destaque"],
            font=ctk.CTkFont(size=26, weight="bold"),
        )

        self.icone_label.grid(row=0, column=0, rowspan=2, padx=(18, 12), pady=18)

        self.titulo_label = ctk.CTkLabel(
            self,
            text=titulo,
            text_color=CORES["texto_secundario"],
            font=ctk.CTkFont(size=12),
            anchor="w",
        )

        self.titulo_label.grid(row=0, column=1, sticky="sw", padx=(0, 15), pady=(15, 0))

        self.valor_label = ctk.CTkLabel(
            self,
            text=str(valor),
            text_color=CORES["texto"],
            font=ctk.CTkFont(size=24, weight="bold"),
            anchor="w",
        )

        self.valor_label.grid(row=1, column=1, sticky="nw", padx=(0, 15), pady=(0, 15))

    def atualizar_valor(self, valor):

        self.valor_label.configure(text=str(valor))


class BotaoPrincipal(ctk.CTkButton):

    def __init__(self, master, texto, comando=None, **kwargs):

        super().__init__(
            master,
            text=texto,
            command=comando,
            height=40,
            corner_radius=8,
            fg_color=CORES["destaque"],
            hover_color=CORES["destaque_hover"],
            text_color=CORES["texto_botao"],
            font=ctk.CTkFont(size=13, weight="bold"),
            **kwargs
        )


class TituloSecao(ctk.CTkLabel):

    def __init__(self, master, texto, **kwargs):

        super().__init__(
            master,
            text=texto,
            text_color=CORES["texto"],
            font=ctk.CTkFont(size=18, weight="bold"),
            anchor="w",
            **kwargs
        )


class Mensagem(ctk.CTkLabel):

    def __init__(self, master, texto, tipo="normal", **kwargs):

        if tipo == "erro":
            cor = CORES["erro"]

        elif tipo == "alerta":
            cor = CORES["alerta"]

        else:
            cor = CORES["texto_secundario"]

        super().__init__(
            master,
            text=texto,
            text_color=cor,
            font=ctk.CTkFont(size=13),
            justify="center",
            **kwargs
        )
