import customtkinter as ctk

from interface.tema import CORES


class CardIndicador(ctk.CTkFrame):
    """
    Cartão para apresentar indicadores e totais do sistema.
    Mantém a compatibilidade com CardIndicador(master, titulo, valor, icone).
    """

    def __init__(
        self,
        master,
        titulo,
        valor="0",
        icone="",
        **kwargs
    ):
        kwargs.setdefault("fg_color", CORES["card"])
        kwargs.setdefault("corner_radius", 14)
        kwargs.setdefault("border_width", 1)
        kwargs.setdefault("border_color", CORES["borda"])

        super().__init__(master, **kwargs)

        self.grid_columnconfigure(1, weight=1)

        # Detalhe dourado lateral
        self.detalhe = ctk.CTkFrame(
            self,
            width=4,
            fg_color=CORES["destaque"],
            corner_radius=3,
        )
        self.detalhe.grid(
            row=0,
            column=0,
            rowspan=2,
            sticky="nsw",
            padx=(0, 14),
            pady=15,
        )

        # Ícone ou símbolo
        self.icone_label = ctk.CTkLabel(
            self,
            text=icone,
            text_color=CORES["destaque_claro"],
            font=ctk.CTkFont(
                family="Segoe UI",
                size=25,
                weight="bold",
            ),
            width=38,
        )
        self.icone_label.grid(
            row=0,
            column=1,
            rowspan=2,
            sticky="w",
            padx=(0, 12),
            pady=16,
        )

        # Título
        self.titulo_label = ctk.CTkLabel(
            self,
            text=titulo,
            text_color=CORES["texto_secundario"],
            font=ctk.CTkFont(
                family="Segoe UI",
                size=12,
                weight="normal",
            ),
            anchor="w",
        )
        self.titulo_label.grid(
            row=0,
            column=2,
            sticky="sw",
            padx=(0, 18),
            pady=(17, 3),
        )

        # Valor principal
        self.valor_label = ctk.CTkLabel(
            self,
            text=str(valor),
            text_color=CORES["texto"],
            font=ctk.CTkFont(
                family="Segoe UI",
                size=28,
                weight="bold",
            ),
            anchor="w",
        )
        self.valor_label.grid(
            row=1,
            column=2,
            sticky="nw",
            padx=(0, 18),
            pady=(0, 17),
        )

    def atualizar_valor(self, valor):
        """Atualiza o número apresentado no cartão."""
        self.valor_label.configure(text=str(valor))

    def atualizar_titulo(self, titulo):
        """Atualiza o título do cartão."""
        self.titulo_label.configure(text=str(titulo))


class BotaoPrincipal(ctk.CTkButton):
    """
    Botão principal com a cor dourada da identidade GAGC.
    """

    def __init__(
        self,
        master,
        texto,
        comando=None,
        **kwargs
    ):
        kwargs.setdefault("height", 40)
        kwargs.setdefault("corner_radius", 9)
        kwargs.setdefault("fg_color", CORES["destaque"])
        kwargs.setdefault("hover_color", CORES["destaque_hover"])
        kwargs.setdefault("text_color", CORES["texto_botao"])
        kwargs.setdefault(
            "font",
            ctk.CTkFont(
                family="Segoe UI",
                size=13,
                weight="bold",
            ),
        )
        kwargs.setdefault("border_width", 0)

        super().__init__(
            master,
            text=texto,
            command=comando,
            **kwargs
        )


class TituloSecao(ctk.CTkLabel):
    """
    Título padronizado para as seções da aplicação.
    """

    def __init__(
        self,
        master,
        texto,
        **kwargs
    ):
        kwargs.setdefault("text_color", CORES["texto"])
        kwargs.setdefault(
            "font",
            ctk.CTkFont(
                family="Segoe UI",
                size=19,
                weight="bold",
            ),
        )
        kwargs.setdefault("anchor", "w")

        super().__init__(
            master,
            text=texto,
            **kwargs
        )


class Mensagem(ctk.CTkLabel):
    """
    Mensagens padronizadas de informação, erro e alerta.

    Tipos aceitos: normal, erro, alerta e sucesso.
    """

    def __init__(
        self,
        master,
        texto,
        tipo="normal",
        **kwargs
    ):
        cores_por_tipo = {
            "normal": CORES["texto_secundario"],
            "erro": CORES["erro"],
            "alerta": CORES["alerta"],
            "sucesso": CORES["sucesso"],
        }

        cor = cores_por_tipo.get(
            tipo,
            CORES["texto_secundario"],
        )

        kwargs.setdefault("text_color", cor)
        kwargs.setdefault(
            "font",
            ctk.CTkFont(
                family="Segoe UI",
                size=13,
            ),
        )
        kwargs.setdefault("justify", "center")
        kwargs.setdefault("wraplength", 600)

        super().__init__(
            master,
            text=texto,
            **kwargs
        )