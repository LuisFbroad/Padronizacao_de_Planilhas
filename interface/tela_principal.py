import customtkinter as ctk
from tkinter import messagebox

from interface.tema import CORES
from interface.componentes import CardIndicador, Mensagem

from src.database.repository import (
    listar_areas,
    listar_ranking,
    contar_total_processos,
    contar_total_pessoas,
)


class TelaPrincipal(ctk.CTkFrame):

    def __init__(self, master, **kwargs):

        super().__init__(master, fg_color=CORES["fundo"], **kwargs)

        self.areas = []
        self.area_selecionada = None
        self.tipo_indicacao_selecionado = "Todas"
        self.tela_atual = None

        self.criar_interface()
        self.carregar_areas()
        self.mostrar_dashboard()

    def criar_interface(self):

        self.sidebar = ctk.CTkFrame(
            self, width=220, fg_color=CORES["sidebar"], corner_radius=0
        )

        self.sidebar.pack(side="left", fill="y")

        self.sidebar.pack_propagate(False)

        self.logo = ctk.CTkLabel(
            self.sidebar,
            text="GAGC",
            text_color=CORES["destaque"],
            font=ctk.CTkFont(size=30, weight="bold"),
        )

        self.logo.pack(pady=(30, 5))

        self.subtitulo_logo = ctk.CTkLabel(
            self.sidebar,
            text="SISTEMA",
            text_color=CORES["texto_claro"],
            font=ctk.CTkFont(size=11, weight="bold"),
        )

        self.subtitulo_logo.pack(pady=(0, 30))

        self.criar_botao_menu("Dashboard", self.mostrar_dashboard)

        self.criar_botao_menu("Indicadores", self.mostrar_indicadores)

        self.criar_botao_menu("Relatórios", self.mostrar_relatorios)

        self.espaco_sidebar = ctk.CTkFrame(self.sidebar, fg_color="transparent")

        self.espaco_sidebar.pack(fill="both", expand=True)

        self.area_principal = ctk.CTkFrame(
            self, fg_color=CORES["fundo"], corner_radius=0
        )

        self.area_principal.pack(side="left", fill="both", expand=True)

    def criar_botao_menu(self, texto, comando):

        botao = ctk.CTkButton(
            self.sidebar,
            text=texto,
            command=comando,
            height=42,
            corner_radius=8,
            fg_color="transparent",
            hover_color=CORES["sidebar_hover"],
            text_color=CORES["texto_claro"],
            anchor="w",
            font=ctk.CTkFont(size=13),
        )

        botao.pack(padx=12, pady=3, fill="x")

        return botao

    def limpar_area(self):

        for widget in self.area_principal.winfo_children():
            widget.destroy()

    def criar_cabecalho(self, titulo, subtitulo=""):

        frame = ctk.CTkFrame(self.area_principal, fg_color="transparent")

        frame.pack(fill="x", padx=30, pady=(25, 10))

        label_titulo = ctk.CTkLabel(
            frame,
            text=titulo,
            text_color=CORES["texto"],
            font=ctk.CTkFont(size=27, weight="bold"),
        )

        label_titulo.pack(anchor="w")

        if subtitulo:

            label_subtitulo = ctk.CTkLabel(
                frame,
                text=subtitulo,
                text_color=CORES["texto_secundario"],
                font=ctk.CTkFont(size=13),
            )

            label_subtitulo.pack(anchor="w", pady=(3, 0))

    def carregar_areas(self):

        try:

            self.areas = listar_areas()

            if self.areas:
                self.area_selecionada = self.areas[0]

        except Exception as erro:

            messagebox.showerror(
                "Erro", f"Não foi possível carregar as áreas:\n\n{erro}"
            )

    def mostrar_dashboard(self):

        self.tela_atual = "dashboard"

        self.limpar_area()

        self.criar_cabecalho("Dashboard", "Visão geral das indicações")

        cards = ctk.CTkFrame(self.area_principal, fg_color="transparent")

        cards.pack(fill="x", padx=30, pady=(10, 20))

        cards.grid_columnconfigure(0, weight=1)

        cards.grid_columnconfigure(1, weight=1)

        cards.grid_columnconfigure(2, weight=1)

        self.card_processos = CardIndicador(
            cards, titulo="Processos", valor=self.obter_total_processos(), icone="▣"
        )

        self.card_processos.grid(row=0, column=0, padx=(0, 10), sticky="ew")

        self.card_pessoas = CardIndicador(
            cards, titulo="Pessoas", valor=self.obter_total_pessoas(), icone="◆"
        )

        self.card_pessoas.grid(row=0, column=1, padx=10, sticky="ew")

        self.card_areas = CardIndicador(
            cards, titulo="Áreas", valor=str(len(self.areas)), icone="▤"
        )

        self.card_areas.grid(row=0, column=2, padx=(10, 0), sticky="ew")

        self.criar_filtros()

        self.criar_area_ranking()

        self.atualizar_ranking_banco()

    def criar_filtros(self):

        filtro_container = ctk.CTkFrame(
            self.area_principal,
            fg_color=CORES["card"],
            corner_radius=12,
            border_width=1,
            border_color=CORES["borda"],
        )

        filtro_container.pack(fill="x", padx=30, pady=(0, 15))

        filtros = ctk.CTkFrame(filtro_container, fg_color="transparent")

        filtros.pack(fill="x", padx=20, pady=15)

        filtros.grid_columnconfigure(0, weight=1)

        filtros.grid_columnconfigure(1, weight=1)

        area_frame = ctk.CTkFrame(filtros, fg_color="transparent")

        area_frame.grid(row=0, column=0, padx=(0, 10), sticky="ew")

        label_area = ctk.CTkLabel(
            area_frame,
            text="Área",
            text_color=CORES["texto"],
            font=ctk.CTkFont(size=14, weight="bold"),
        )

        label_area.pack(anchor="w", pady=(0, 6))

        self.combo_areas = ctk.CTkComboBox(
            area_frame,
            values=[area.nome for area in self.areas],
            height=36,
            command=self.selecionar_area,
        )

        self.combo_areas.pack(fill="x")

        if self.area_selecionada:

            self.combo_areas.set(self.area_selecionada.nome)

        tipo_frame = ctk.CTkFrame(filtros, fg_color="transparent")

        tipo_frame.grid(row=0, column=1, padx=(10, 0), sticky="ew")

        label_tipo = ctk.CTkLabel(
            tipo_frame,
            text="Tipo de indicação",
            text_color=CORES["texto"],
            font=ctk.CTkFont(size=14, weight="bold"),
        )

        label_tipo.pack(anchor="w", pady=(0, 6))

        self.tipos_indicacao = [
            "Todas",
            "Primária",
            "Secundária",
            "Terciária",
            "Quaternária",
            "Final",
        ]

        self.combo_tipos = ctk.CTkComboBox(
            tipo_frame,
            values=self.tipos_indicacao,
            height=36,
            command=self.selecionar_tipo_indicacao,
        )

        self.combo_tipos.pack(fill="x")

        self.combo_tipos.set(self.tipo_indicacao_selecionado)

    def criar_area_ranking(self):

        ranking_container = ctk.CTkFrame(
            self.area_principal,
            fg_color=CORES["card"],
            corner_radius=12,
            border_width=1,
            border_color=CORES["borda"],
        )

        ranking_container.pack(fill="both", expand=True, padx=30, pady=(0, 30))

        titulo_ranking = ctk.CTkLabel(
            ranking_container,
            text="Ranking de indicações",
            text_color=CORES["texto"],
            font=ctk.CTkFont(size=17, weight="bold"),
        )

        titulo_ranking.pack(anchor="w", padx=20, pady=(15, 10))

        self.ranking_scroll = ctk.CTkScrollableFrame(
            ranking_container, fg_color="transparent"
        )

        self.ranking_scroll.pack(fill="both", expand=True, padx=15, pady=(0, 15))

    def selecionar_area(self, nome_area):

        for area in self.areas:

            if area.nome == nome_area:

                self.area_selecionada = area
                break

        self.atualizar_cards()

        self.atualizar_ranking_banco()

    def selecionar_tipo_indicacao(self, tipo):

        self.tipo_indicacao_selecionado = tipo

        self.atualizar_cards()

        self.atualizar_ranking_banco()

    def atualizar_cards(self):

        if not hasattr(self, "card_processos"):
            return

        self.card_processos.atualizar_valor(self.obter_total_processos())

        self.card_pessoas.atualizar_valor(self.obter_total_pessoas())

    def obter_total_processos(self):

        if self.area_selecionada is None:
            return "0"

        try:

            total = contar_total_processos(
                area_id=self.area_selecionada.id,
                tipo_indicacao=self.tipo_indicacao_selecionado,
            )

            return str(total)

        except Exception:

            return "0"

    def obter_total_pessoas(self):

        if self.area_selecionada is None:
            return "0"

        try:

            total = contar_total_pessoas(
                area_id=self.area_selecionada.id,
                tipo_indicacao=self.tipo_indicacao_selecionado,
            )

            return str(total)

        except Exception:

            return "0"

    def atualizar_ranking_banco(self):

        if not hasattr(self, "ranking_scroll"):
            return

        for widget in self.ranking_scroll.winfo_children():
            widget.destroy()

        if self.area_selecionada is None:

            Mensagem(
                self.ranking_scroll, "Nenhuma área selecionada.", tipo="alerta"
            ).pack(pady=30)

            return

        try:

            ranking = listar_ranking(
                self.area_selecionada.id, self.tipo_indicacao_selecionado
            )

        except Exception as erro:

            Mensagem(
                self.ranking_scroll, f"Erro ao consultar o banco:\n{erro}", tipo="erro"
            ).pack(pady=30)

            return

        if not ranking:

            Mensagem(
                self.ranking_scroll, "Nenhuma indicação encontrada.", tipo="alerta"
            ).pack(pady=30)

            return

        self.mostrar_ranking_banco(ranking)

    def mostrar_ranking_banco(self, ranking):

        for indice, (nome, quantidade) in enumerate(ranking):

            linha_frame = ctk.CTkFrame(
                self.ranking_scroll,
                fg_color=CORES["fundo_secundario"],
                corner_radius=8,
                border_width=1,
                border_color=CORES["borda"],
            )

            linha_frame.pack(fill="x", pady=4, padx=3)

            posicao = ctk.CTkLabel(
                linha_frame,
                text=f"{indice + 1}º",
                width=55,
                text_color=CORES["destaque"],
                font=ctk.CTkFont(size=14, weight="bold"),
            )

            posicao.pack(side="left", padx=(10, 5))

            nome_label = ctk.CTkLabel(
                linha_frame,
                text=str(nome),
                text_color=CORES["texto"],
                font=ctk.CTkFont(size=14, weight="bold"),
                anchor="w",
            )

            nome_label.pack(side="left", fill="x", expand=True, padx=10)

            quantidade_label = ctk.CTkLabel(
                linha_frame,
                text=f"{quantidade} processos",
                text_color=CORES["texto_secundario"],
                font=ctk.CTkFont(size=13),
            )

            quantidade_label.pack(side="right", padx=15)

    def mostrar_indicadores(self):

        self.tela_atual = "indicadores"

        self.limpar_area()

        self.criar_cabecalho("Indicadores", "Análise das indicações cadastradas")

        container = ctk.CTkFrame(
            self.area_principal,
            fg_color=CORES["card"],
            corner_radius=12,
            border_width=1,
            border_color=CORES["borda"],
        )

        container.pack(fill="both", expand=True, padx=30, pady=(0, 30))

        Mensagem(
            container, "Os indicadores serão desenvolvidos nesta etapa.", tipo="normal"
        ).pack(pady=50)

    def mostrar_relatorios(self):

        self.tela_atual = "relatorios"

        self.limpar_area()

        self.criar_cabecalho("Relatórios", "Área destinada aos relatórios do sistema")

        container = ctk.CTkFrame(
            self.area_principal,
            fg_color=CORES["card"],
            corner_radius=12,
            border_width=1,
            border_color=CORES["borda"],
        )

        container.pack(fill="both", expand=True, padx=30, pady=(0, 30))

        Mensagem(
            container, "Módulo de relatórios em desenvolvimento.", tipo="normal"
        ).pack(pady=50)
