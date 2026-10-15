import customtkinter as ctk
from tkinter import messagebox
from sqlalchemy import func, extract, case

from interface.tema import CORES
from interface.componentes import CardIndicador, Mensagem

from src.database.repository import (
    listar_anos_disponiveis,
    listar_areas,
    listar_ranking,
    contar_total_processos,
    contar_total_pessoas,
)

from src.database.connection import SessionLocal
from src.database.models import Pessoa, Indicacao


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
            self,
            width=220,
            fg_color=CORES["sidebar"],
            corner_radius=0,
        )
        self.sidebar.pack(side="left", fill="y")
        self.sidebar.pack_propagate(False)

        ctk.CTkLabel(
            self.sidebar,
            text="GAGC",
            text_color=CORES["destaque"],
            font=ctk.CTkFont(size=30, weight="bold"),
        ).pack(pady=(30, 5))

        ctk.CTkLabel(
            self.sidebar,
            text="SISTEMA",
            text_color=CORES["texto_claro"],
            font=ctk.CTkFont(size=11, weight="bold"),
        ).pack(pady=(0, 30))

        self.criar_botao_menu("Dashboard", self.mostrar_dashboard)
        self.criar_botao_menu("Indicadores", self.mostrar_indicadores)
        self.criar_botao_menu("Relatórios", self.mostrar_relatorios)

        ctk.CTkFrame(
            self.sidebar,
            fg_color="transparent",
        ).pack(fill="both", expand=True)

        self.area_principal = ctk.CTkFrame(
            self,
            fg_color=CORES["fundo"],
            corner_radius=0,
        )
        self.area_principal.pack(
            side="left",
            fill="both",
            expand=True,
        )

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
        frame = ctk.CTkFrame(
            self.area_principal,
            fg_color="transparent",
        )
        frame.pack(fill="x", padx=30, pady=(25, 10))

        ctk.CTkLabel(
            frame,
            text=titulo,
            text_color=CORES["texto"],
            font=ctk.CTkFont(size=27, weight="bold"),
        ).pack(anchor="w")

        if subtitulo:
            ctk.CTkLabel(
                frame,
                text=subtitulo,
                text_color=CORES["texto_secundario"],
                font=ctk.CTkFont(size=13),
            ).pack(anchor="w", pady=(3, 0))

    def carregar_areas(self):
        try:
            self.areas = listar_areas()

            if self.areas:
                self.area_selecionada = self.areas[0]

        except Exception as erro:
            messagebox.showerror(
                "Erro",
                f"Não foi possível carregar as áreas:\n\n{erro}",
            )

    # =========================================================
    # DASHBOARD
    # =========================================================

    def mostrar_dashboard(self):
        self.tela_atual = "dashboard"
        self.limpar_area()

        self.criar_cabecalho(
            "Dashboard",
            "Visão geral das indicações",
        )

        cards = ctk.CTkFrame(
            self.area_principal,
            fg_color="transparent",
        )
        cards.pack(fill="x", padx=30, pady=(10, 20))

        for coluna in range(3):
            cards.grid_columnconfigure(coluna, weight=1)

        self.card_processos = CardIndicador(
            cards,
            titulo="Processos",
            valor=self.obter_total_processos(),
            icone="▣",
        )
        self.card_processos.grid(row=0, column=0, padx=(0, 10), sticky="ew")

        self.card_pessoas = CardIndicador(
            cards,
            titulo="Pessoas",
            valor=self.obter_total_pessoas(),
            icone="◆",
        )
        self.card_pessoas.grid(row=0, column=1, padx=10, sticky="ew")

        self.card_areas = CardIndicador(
            cards,
            titulo="Áreas",
            valor=str(len(self.areas)),
            icone="▤",
        )
        self.card_areas.grid(row=0, column=2, padx=(10, 0), sticky="ew")

        self.criar_filtros()
        self.criar_area_ranking()
        self.atualizar_ranking_banco()

    def criar_filtros(self):
        container = ctk.CTkFrame(
            self.area_principal,
            fg_color=CORES["card"],
            corner_radius=12,
            border_width=1,
            border_color=CORES["borda"],
        )
        container.pack(fill="x", padx=30, pady=(0, 15))

        filtros = ctk.CTkFrame(
            container,
            fg_color="transparent",
        )
        filtros.pack(fill="x", padx=20, pady=15)

        filtros.grid_columnconfigure(0, weight=1)
        filtros.grid_columnconfigure(1, weight=1)

        area_frame = ctk.CTkFrame(
            filtros,
            fg_color="transparent",
        )
        area_frame.grid(row=0, column=0, padx=(0, 10), sticky="ew")

        ctk.CTkLabel(
            area_frame,
            text="Área",
            text_color=CORES["texto"],
            font=ctk.CTkFont(size=14, weight="bold"),
        ).pack(anchor="w", pady=(0, 6))

        self.combo_areas = ctk.CTkComboBox(
            area_frame,
            values=[area.nome for area in self.areas],
            height=36,
            command=self.selecionar_area,
        )
        self.combo_areas.pack(fill="x")

        if self.area_selecionada:
            self.combo_areas.set(self.area_selecionada.nome)

        tipo_frame = ctk.CTkFrame(
            filtros,
            fg_color="transparent",
        )
        tipo_frame.grid(row=0, column=1, padx=(10, 0), sticky="ew")

        ctk.CTkLabel(
            tipo_frame,
            text="Tipo de indicação",
            text_color=CORES["texto"],
            font=ctk.CTkFont(size=14, weight="bold"),
        ).pack(anchor="w", pady=(0, 6))

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
        container = ctk.CTkFrame(
            self.area_principal,
            fg_color=CORES["card"],
            corner_radius=12,
            border_width=1,
            border_color=CORES["borda"],
        )
        container.pack(
            fill="both",
            expand=True,
            padx=30,
            pady=(0, 30),
        )

        ctk.CTkLabel(
            container,
            text="Ranking de indicações",
            text_color=CORES["texto"],
            font=ctk.CTkFont(size=17, weight="bold"),
        ).pack(anchor="w", padx=20, pady=(15, 10))

        self.ranking_scroll = ctk.CTkScrollableFrame(
            container,
            fg_color="transparent",
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
            return str(
                contar_total_processos(
                    area_id=self.area_selecionada.id,
                    tipo_indicacao=self.tipo_indicacao_selecionado,
                )
            )
        except Exception:
            return "0"

    def obter_total_pessoas(self):
        if self.area_selecionada is None:
            return "0"

        try:
            return str(
                contar_total_pessoas(
                    area_id=self.area_selecionada.id,
                    tipo_indicacao=self.tipo_indicacao_selecionado,
                )
            )
        except Exception:
            return "0"

    def atualizar_ranking_banco(self):
        if not hasattr(self, "ranking_scroll"):
            return

        for widget in self.ranking_scroll.winfo_children():
            widget.destroy()

        if self.area_selecionada is None:
            Mensagem(
                self.ranking_scroll,
                "Nenhuma área selecionada.",
                tipo="alerta",
            ).pack(pady=30)
            return

        try:
            ranking = listar_ranking(
                self.area_selecionada.id,
                self.tipo_indicacao_selecionado,
            )
        except Exception as erro:
            Mensagem(
                self.ranking_scroll,
                f"Erro ao consultar o banco:\n{erro}",
                tipo="erro",
            ).pack(pady=30)
            return

        if not ranking:
            Mensagem(
                self.ranking_scroll,
                "Nenhuma indicação encontrada.",
                tipo="alerta",
            ).pack(pady=30)
            return

        for indice, (nome, quantidade) in enumerate(ranking):
            linha = ctk.CTkFrame(
                self.ranking_scroll,
                fg_color=CORES["fundo_secundario"],
                corner_radius=8,
                border_width=1,
                border_color=CORES["borda"],
            )
            linha.pack(fill="x", pady=4, padx=3)

            ctk.CTkLabel(
                linha,
                text=f"{indice + 1}º",
                width=55,
                text_color=CORES["destaque"],
                font=ctk.CTkFont(size=14, weight="bold"),
            ).pack(side="left", padx=(10, 5))

            ctk.CTkLabel(
                linha,
                text=str(nome),
                text_color=CORES["texto"],
                font=ctk.CTkFont(size=14, weight="bold"),
                anchor="w",
            ).pack(side="left", fill="x", expand=True, padx=10)

            ctk.CTkLabel(
                linha,
                text=f"{quantidade} processos",
                text_color=CORES["texto_secundario"],
                font=ctk.CTkFont(size=13),
            ).pack(side="right", padx=15)

    # =========================================================
    # INDICADORES
    # =========================================================

    def mostrar_indicadores(self):
        self.tela_atual = "indicadores"
        self.limpar_area()

        self.criar_cabecalho(
            "Indicadores",
            "Análise das indicações por ano, mês e semana",
        )

        container = ctk.CTkFrame(
            self.area_principal,
            fg_color="transparent",
        )
        container.pack(fill="both", expand=True, padx=30, pady=(0, 25))

        filtros = ctk.CTkFrame(
            container,
            fg_color=CORES["card"],
            corner_radius=12,
            border_width=1,
            border_color=CORES["borda"],
        )
        filtros.pack(fill="x", pady=(0, 15))

        for coluna in range(3):
            filtros.grid_columnconfigure(coluna, weight=1)

        ctk.CTkLabel(
            filtros,
            text="Ano",
            text_color=CORES["texto"],
        ).grid(row=0, column=0, padx=15, pady=(15, 5), sticky="w")

        ctk.CTkLabel(
            filtros,
            text="Mês",
            text_color=CORES["texto"],
        ).grid(row=0, column=1, padx=15, pady=(15, 5), sticky="w")

        ctk.CTkLabel(
            filtros,
            text="Semana",
            text_color=CORES["texto"],
        ).grid(row=0, column=2, padx=15, pady=(15, 5), sticky="w")

        self.meses_indicadores = {
            "Todos": None,
            "Janeiro": 1,
            "Fevereiro": 2,
            "Março": 3,
            "Abril": 4,
            "Maio": 5,
            "Junho": 6,
            "Julho": 7,
            "Agosto": 8,
            "Setembro": 9,
            "Outubro": 10,
            "Novembro": 11,
            "Dezembro": 12,
        }

        anos = listar_anos_disponiveis()
        valores_anos = ["Todos"] + [str(ano) for ano in anos]

        self.combo_ano_indicadores = ctk.CTkComboBox(
            filtros,
            values=valores_anos,
            command=self.alterar_filtro_ano,
            height=36,
        )
        self.combo_ano_indicadores.grid(
            row=1, column=0, padx=15, pady=(0, 15), sticky="ew"
        )
        self.combo_ano_indicadores.set("Todos")

        self.combo_mes_indicadores = ctk.CTkComboBox(
            filtros,
            values=list(self.meses_indicadores.keys()),
            command=self.alterar_filtro_mes,
            height=36,
        )
        self.combo_mes_indicadores.grid(
            row=1, column=1, padx=15, pady=(0, 15), sticky="ew"
        )
        self.combo_mes_indicadores.set("Todos")

        self.combo_semana_indicadores = ctk.CTkComboBox(
            filtros,
            values=["Todas", "1ª", "2ª", "3ª", "4ª"],
            command=self.alterar_filtro_semana,
            height=36,
        )
        self.combo_semana_indicadores.grid(
            row=1, column=2, padx=15, pady=(0, 15), sticky="ew"
        )
        self.combo_semana_indicadores.set("Todas")

        cards = ctk.CTkFrame(
            container,
            fg_color="transparent",
        )
        cards.pack(fill="x", pady=(0, 15))
        cards.grid_columnconfigure((0, 1), weight=1)

        self.card_indicadores_processos = CardIndicador(
            cards,
            titulo="Processos",
            valor="0",
        )
        self.card_indicadores_processos.grid(row=0, column=0, padx=(0, 8), sticky="ew")

        self.card_indicadores_pessoas = CardIndicador(
            cards,
            titulo="Pessoas com indicações",
            valor="0",
        )
        self.card_indicadores_pessoas.grid(row=0, column=1, padx=(8, 0), sticky="ew")

        ranking_container = ctk.CTkFrame(
            container,
            fg_color=CORES["card"],
            corner_radius=12,
            border_width=1,
            border_color=CORES["borda"],
        )
        ranking_container.pack(fill="both", expand=True)

        ctk.CTkLabel(
            ranking_container,
            text="Ranking de indicações",
            text_color=CORES["texto"],
            font=ctk.CTkFont(size=17, weight="bold"),
        ).pack(anchor="w", padx=20, pady=(15, 10))

        self.ranking_indicadores = ctk.CTkScrollableFrame(
            ranking_container,
            fg_color="transparent",
        )
        self.ranking_indicadores.pack(fill="both", expand=True, padx=15, pady=(0, 15))

        self.atualizar_indicadores()

    def obter_periodo_indicadores(self):
        ano_texto = self.combo_ano_indicadores.get()
        mes_texto = self.combo_mes_indicadores.get()
        semana_texto = self.combo_semana_indicadores.get()

        ano = int(ano_texto) if ano_texto != "Todos" else None
        mes = self.meses_indicadores.get(mes_texto)

        semanas = {
            "1ª": 1,
            "2ª": 2,
            "3ª": 3,
            "4ª": 4,
        }
        semana = semanas.get(semana_texto)

        return ano, mes, semana

    def alterar_filtro_ano(self, valor):
        self.atualizar_indicadores()

    def alterar_filtro_mes(self, valor):
        self.atualizar_indicadores()

    def alterar_filtro_semana(self, valor):
        self.atualizar_indicadores()

    def aplicar_filtros_periodo(
        self,
        consulta,
        ano=None,
        mes=None,
        semana=None,
    ):
        if ano is not None:
            consulta = consulta.filter(extract("year", Indicacao.data_indicacao) == ano)

        if mes is not None:
            consulta = consulta.filter(
                extract("month", Indicacao.data_indicacao) == mes
            )

        if semana is not None:
            dia = extract("day", Indicacao.data_indicacao)

            if semana == 1:
                consulta = consulta.filter(dia >= 1, dia <= 7)
            elif semana == 2:
                consulta = consulta.filter(dia >= 8, dia <= 14)
            elif semana == 3:
                consulta = consulta.filter(dia >= 15, dia <= 21)
            elif semana == 4:
                consulta = consulta.filter(dia >= 22)

        return consulta

    def aplicar_filtros_indicadores(self, consulta):
        if self.area_selecionada is not None:
            consulta = consulta.filter(Indicacao.area_id == self.area_selecionada.id)

        if self.tipo_indicacao_selecionado != "Todas":
            consulta = consulta.filter(
                Indicacao.tipo_indicacao == self.tipo_indicacao_selecionado
            )

        return consulta

    def contar_processos_periodo(self, ano=None, mes=None, semana=None):
        session = SessionLocal()

        try:
            consulta = session.query(
                func.count(func.distinct(Indicacao.processo))
            ).filter(Indicacao.processo.isnot(None))

            consulta = self.aplicar_filtros_indicadores(consulta)
            consulta = self.aplicar_filtros_periodo(consulta, ano, mes, semana)

            return consulta.scalar() or 0

        finally:
            session.close()

    def contar_pessoas_periodo(self, ano=None, mes=None, semana=None):
        session = SessionLocal()

        try:
            consulta = session.query(
                func.count(func.distinct(Indicacao.pessoa_id))
            ).filter(Indicacao.processo.isnot(None))

            consulta = self.aplicar_filtros_indicadores(consulta)
            consulta = self.aplicar_filtros_periodo(consulta, ano, mes, semana)

            return consulta.scalar() or 0

        finally:
            session.close()

    def obter_ranking_indicadores(
        self,
        ano=None,
        mes=None,
        semana=None,
    ):
        session = SessionLocal()

        try:
            consulta = (
                session.query(
                    Pessoa.nome,
                    func.count(func.distinct(Indicacao.processo)).label(
                        "total_processos"
                    ),
                )
                .join(
                    Indicacao,
                    Indicacao.pessoa_id == Pessoa.id,
                )
                .filter(Indicacao.processo.isnot(None))
            )

            consulta = self.aplicar_filtros_indicadores(consulta)
            consulta = self.aplicar_filtros_periodo(consulta, ano, mes, semana)

            return (
                consulta.group_by(Pessoa.id, Pessoa.nome)
                .order_by(
                    func.count(func.distinct(Indicacao.processo)).desc(),
                    Pessoa.nome,
                )
                .all()
            )

        finally:
            session.close()

    def atualizar_indicadores(self):
        if not hasattr(self, "ranking_indicadores"):
            return

        ano, mes, semana = self.obter_periodo_indicadores()

        for widget in self.ranking_indicadores.winfo_children():
            widget.destroy()

        try:
            total_processos = self.contar_processos_periodo(
                ano=ano,
                mes=mes,
                semana=semana,
            )

            total_pessoas = self.contar_pessoas_periodo(
                ano=ano,
                mes=mes,
                semana=semana,
            )

            self.card_indicadores_processos.atualizar_valor(total_processos)
            self.card_indicadores_pessoas.atualizar_valor(total_pessoas)

            ranking = self.obter_ranking_indicadores(
                ano=ano,
                mes=mes,
                semana=semana,
            )

            if not ranking:
                Mensagem(
                    self.ranking_indicadores,
                    "Nenhuma indicação encontrada para esse período.",
                    tipo="alerta",
                ).pack(pady=30)
                return

            for posicao, (nome, quantidade) in enumerate(
                ranking,
                start=1,
            ):
                linha = ctk.CTkFrame(
                    self.ranking_indicadores,
                    fg_color=CORES["fundo_secundario"],
                    corner_radius=8,
                )
                linha.pack(fill="x", pady=4, padx=3)

                ctk.CTkLabel(
                    linha,
                    text=f"{posicao}º",
                    width=55,
                    text_color=CORES["destaque"],
                    font=ctk.CTkFont(size=14, weight="bold"),
                ).pack(side="left", padx=(10, 5))

                ctk.CTkLabel(
                    linha,
                    text=str(nome),
                    text_color=CORES["texto"],
                    font=ctk.CTkFont(size=14, weight="bold"),
                    anchor="w",
                ).pack(side="left", fill="x", expand=True, padx=10)

                ctk.CTkLabel(
                    linha,
                    text=f"{quantidade} processos",
                    text_color=CORES["texto_secundario"],
                ).pack(side="right", padx=15)

        except Exception as erro:
            Mensagem(
                self.ranking_indicadores,
                f"Erro ao carregar indicadores:\n{erro}",
                tipo="erro",
            ).pack(pady=30)

    # =========================================================
    # RELATÓRIOS
    # =========================================================

    def mostrar_relatorios(self):
        self.tela_atual = "relatorios"
        self.limpar_area()

        self.criar_cabecalho(
            "Relatórios",
            "Área destinada aos relatórios do sistema",
        )

        container = ctk.CTkFrame(
            self.area_principal,
            fg_color=CORES["card"],
            corner_radius=12,
            border_width=1,
            border_color=CORES["borda"],
        )
        container.pack(fill="both", expand=True, padx=30, pady=(0, 30))

        Mensagem(
            container,
            "Módulo de relatórios em desenvolvimento.",
            tipo="normal",
        ).pack(pady=50)
