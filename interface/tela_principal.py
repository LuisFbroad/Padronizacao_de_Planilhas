import customtkinter as ctk
from tkinter import filedialog, messagebox
from sqlalchemy import func, extract
from openpyxl import Workbook
from openpyxl.styles import Font, PatternFill, Alignment

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
from src.database.models import Area, Pessoa, Indicacao, Processo


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

    # =========================================================
    # ESTRUTURA PRINCIPAL
    # =========================================================

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

        self.criar_filtros_dashboard()
        self.criar_area_ranking()
        self.atualizar_ranking_banco()

    def criar_filtros_dashboard(self):
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
        elif self.areas:
            self.combo_areas.set(self.areas[0].nome)

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
        session = SessionLocal()

        try:
            if self.area_selecionada is None:
                return "0"

            nome_area = (self.area_selecionada.nome or "").strip().casefold()

            if "projet" in nome_area:
                consulta = session.query(
                    func.coalesce(func.max(Processo.quantidade), 0)
                ).filter(Processo.area_id == self.area_selecionada.id)

                return str(consulta.scalar() or 0)

            consulta = session.query(
                func.coalesce(func.max(Indicacao.quantidade), 0)
            ).filter(Indicacao.area_id == self.area_selecionada.id)

            if self.tipo_indicacao_selecionado != "Todas":
                consulta = consulta.filter(
                    Indicacao.tipo_indicacao == self.tipo_indicacao_selecionado
                )

            return str(consulta.scalar() or 0)

        except Exception as erro:
            print(f"Erro ao contar processos: {erro}")
            return "0"

        finally:
            session.close()

    def obter_total_pessoas(self):
        try:
            return str(
                contar_total_pessoas(
                    area_id=(
                        self.area_selecionada.id if self.area_selecionada else None
                    ),
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
                text=f"{quantidade} indicações",
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

        for coluna, titulo in enumerate(["Ano", "Mês", "Semana"]):
            ctk.CTkLabel(
                filtros,
                text=titulo,
                text_color=CORES["texto"],
            ).grid(
                row=0,
                column=coluna,
                padx=15,
                pady=(15, 5),
                sticky="w",
            )

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
            command=self.alterar_filtro_indicadores,
            height=36,
        )
        self.combo_ano_indicadores.grid(
            row=1, column=0, padx=15, pady=(0, 15), sticky="ew"
        )
        self.combo_ano_indicadores.set("Todos")

        self.combo_mes_indicadores = ctk.CTkComboBox(
            filtros,
            values=list(self.meses_indicadores.keys()),
            command=self.alterar_filtro_indicadores,
            height=36,
        )
        self.combo_mes_indicadores.grid(
            row=1, column=1, padx=15, pady=(0, 15), sticky="ew"
        )
        self.combo_mes_indicadores.set("Todos")

        self.combo_semana_indicadores = ctk.CTkComboBox(
            filtros,
            values=["Todas", "1ª", "2ª", "3ª", "4ª"],
            command=self.alterar_filtro_indicadores,
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

    def alterar_filtro_indicadores(self, valor=None):
        self.atualizar_indicadores()

    def aplicar_filtros_periodo(
        self,
        consulta,
        ano=None,
        mes=None,
        semana=None,
        campo_data=None,
    ):
        data = campo_data or Indicacao.data_indicacao

        if ano is not None:
            consulta = consulta.filter(extract("year", data) == ano)

        if mes is not None:
            consulta = consulta.filter(extract("month", data) == mes)

        if semana is not None:
            limites = {
                1: (1, 7),
                2: (8, 14),
                3: (15, 21),
                4: (22, 31),
            }
            inicio, fim = limites[semana]
            dia = extract("day", data)

            consulta = consulta.filter(
                dia >= inicio,
                dia <= fim,
            )

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
            if self.area_selecionada is None:
                return 0

            nome_area = (self.area_selecionada.nome or "").strip().casefold()

            if "projet" in nome_area:
                consulta = session.query(
                    func.coalesce(func.max(Processo.quantidade), 0)
                ).filter(Processo.area_id == self.area_selecionada.id)

                consulta = self.aplicar_filtros_periodo(
                    consulta,
                    ano,
                    mes,
                    semana,
                    campo_data=Processo.data_processo,
                )

                if self.tipo_indicacao_selecionado != "Todas":
                    return 0

                return consulta.scalar() or 0

            consulta = session.query(func.coalesce(func.max(Indicacao.quantidade), 0))

            consulta = self.aplicar_filtros_indicadores(consulta)
            consulta = self.aplicar_filtros_periodo(consulta, ano, mes, semana)

            return consulta.scalar() or 0

        finally:
            session.close()

    def contar_pessoas_periodo(self, ano=None, mes=None, semana=None):
        session = SessionLocal()

        try:
            consulta = session.query(func.count(func.distinct(Indicacao.pessoa_id)))

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
            consulta = session.query(
                Pessoa.nome,
                func.count(Indicacao.id).label("total_indicacoes"),
            ).join(
                Indicacao,
                Indicacao.pessoa_id == Pessoa.id,
            )

            consulta = self.aplicar_filtros_indicadores(consulta)
            consulta = self.aplicar_filtros_periodo(consulta, ano, mes, semana)

            return (
                consulta.group_by(Pessoa.id, Pessoa.nome)
                .order_by(
                    func.count(Indicacao.id).desc(),
                    Pessoa.nome,
                )
                .all()
            )

        finally:
            session.close()

    def atualizar_indicadores(self):
        if not hasattr(self, "ranking_indicadores"):
            return

        for widget in self.ranking_indicadores.winfo_children():
            widget.destroy()

        ano, mes, semana = self.obter_periodo_indicadores()

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

            for posicao, (nome, quantidade) in enumerate(ranking, start=1):
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
                    text=f"{quantidade} indicações",
                    text_color=CORES["texto_secundario"],
                ).pack(side="right", padx=15)

        except Exception as erro:
            Mensagem(
                self.ranking_indicadores,
                f"Erro ao carregar indicadores:\n{erro}",
                tipo="erro",
            ).pack(pady=30)

    # =========================================================
    # RELATÓRIOS POR ÁREA
    # =========================================================

    def mostrar_relatorios(self):
        self.tela_atual = "relatorios"
        self.limpar_area()

        self.criar_cabecalho(
            "Relatórios por Área",
            "Consulte e exporte os resultados por período e tipo de indicação.",
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

        for coluna in range(4):
            filtros.grid_columnconfigure(coluna, weight=1)

        titulos = [
            "Ano",
            "Mês",
            "Semana",
            "Tipo de indicação",
        ]

        for coluna, titulo in enumerate(titulos):
            ctk.CTkLabel(
                filtros,
                text=titulo,
                text_color=CORES["texto"],
            ).grid(
                row=0,
                column=coluna,
                padx=12,
                pady=(15, 5),
                sticky="w",
            )

        self.meses_relatorios = {
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

        self.combo_ano_relatorios = ctk.CTkComboBox(
            filtros,
            values=valores_anos,
            command=self.alterar_filtro_relatorio,
            height=36,
        )
        self.combo_ano_relatorios.grid(
            row=1, column=0, padx=12, pady=(0, 15), sticky="ew"
        )
        self.combo_ano_relatorios.set("Todos")

        self.combo_mes_relatorios = ctk.CTkComboBox(
            filtros,
            values=list(self.meses_relatorios.keys()),
            command=self.alterar_filtro_relatorio,
            height=36,
        )
        self.combo_mes_relatorios.grid(
            row=1, column=1, padx=12, pady=(0, 15), sticky="ew"
        )
        self.combo_mes_relatorios.set("Todos")

        self.combo_semana_relatorios = ctk.CTkComboBox(
            filtros,
            values=["Todas", "1ª", "2ª", "3ª", "4ª"],
            command=self.alterar_filtro_relatorio,
            height=36,
        )
        self.combo_semana_relatorios.grid(
            row=1, column=2, padx=12, pady=(0, 15), sticky="ew"
        )
        self.combo_semana_relatorios.set("Todas")

        self.combo_tipo_relatorios = ctk.CTkComboBox(
            filtros,
            values=[
                "Todas",
                "Primária",
                "Secundária",
                "Terciária",
                "Quaternária",
                "Final",
            ],
            command=self.alterar_filtro_relatorio,
            height=36,
        )
        self.combo_tipo_relatorios.grid(
            row=1, column=3, padx=12, pady=(0, 15), sticky="ew"
        )
        self.combo_tipo_relatorios.set("Todas")

        cards = ctk.CTkFrame(
            container,
            fg_color="transparent",
        )
        cards.pack(fill="x", pady=(0, 15))
        cards.grid_columnconfigure((0, 1), weight=1)

        self.card_relatorio_processos = CardIndicador(
            cards,
            titulo="Total de Processos",
            valor="0",
            icone="▣",
        )
        self.card_relatorio_processos.grid(row=0, column=0, padx=(0, 8), sticky="ew")

        self.card_relatorio_areas = CardIndicador(
            cards,
            titulo="Áreas com Resultados",
            valor="0",
            icone="▤",
        )
        self.card_relatorio_areas.grid(row=0, column=1, padx=(8, 0), sticky="ew")

        tabela_container = ctk.CTkFrame(
            container,
            fg_color=CORES["card"],
            corner_radius=12,
            border_width=1,
            border_color=CORES["borda"],
        )
        tabela_container.pack(fill="both", expand=True)

        cabecalho = ctk.CTkFrame(
            tabela_container,
            fg_color="transparent",
        )
        cabecalho.pack(fill="x", padx=20, pady=(15, 10))

        ctk.CTkLabel(
            cabecalho,
            text="Resumo por área",
            text_color=CORES["texto"],
            font=ctk.CTkFont(size=17, weight="bold"),
        ).pack(side="left")

        ctk.CTkButton(
            cabecalho,
            text="Exportar Excel",
            command=self.exportar_relatorio_excel,
            height=34,
            width=140,
        ).pack(side="right")

        self.tabela_relatorios = ctk.CTkFrame(
            tabela_container,
            fg_color="transparent",
        )
        self.tabela_relatorios.pack(fill="both", expand=True, padx=15, pady=(0, 15))

        self.tabela_relatorios.grid_columnconfigure(0, weight=3)
        self.tabela_relatorios.grid_columnconfigure(1, weight=1)
        self.tabela_relatorios.grid_columnconfigure(2, weight=1)
        self.tabela_relatorios.grid_rowconfigure(1, weight=1)

        cabecalho_tabela = ctk.CTkFrame(
            self.tabela_relatorios,
            fg_color=CORES["fundo_secundario"],
            corner_radius=6,
        )
        cabecalho_tabela.grid(row=0, column=0, columnspan=3, sticky="ew", pady=(0, 5))

        for coluna, titulo in enumerate(["Área", "Processos", "Indicações"]):
            cabecalho_tabela.grid_columnconfigure(
                coluna,
                weight=3 if coluna == 0 else 1,
            )

            ctk.CTkLabel(
                cabecalho_tabela,
                text=titulo,
                text_color=CORES["texto"],
                font=ctk.CTkFont(size=13, weight="bold"),
                anchor="w" if coluna == 0 else "center",
            ).grid(
                row=0,
                column=coluna,
                padx=12,
                pady=10,
                sticky="ew",
            )

        self.linhas_relatorios = ctk.CTkScrollableFrame(
            self.tabela_relatorios,
            fg_color="transparent",
        )
        self.linhas_relatorios.grid(row=1, column=0, columnspan=3, sticky="nsew")

        self.atualizar_relatorio_area()

    def obter_filtros_relatorio(self):
        ano_texto = self.combo_ano_relatorios.get()
        mes_texto = self.combo_mes_relatorios.get()
        semana_texto = self.combo_semana_relatorios.get()
        tipo = self.combo_tipo_relatorios.get()

        ano = int(ano_texto) if ano_texto != "Todos" else None
        mes = self.meses_relatorios.get(mes_texto)

        semanas = {
            "1ª": 1,
            "2ª": 2,
            "3ª": 3,
            "4ª": 4,
        }

        semana = semanas.get(semana_texto)

        return ano, mes, semana, tipo

    def alterar_filtro_relatorio(self, valor=None):
        self.atualizar_relatorio_area()

    def aplicar_filtros_relatorio(
        self,
        consulta,
        ano=None,
        mes=None,
        semana=None,
        tipo="Todas",
    ):
        data = Indicacao.data_indicacao

        if ano is not None:
            consulta = consulta.filter(extract("year", data) == ano)

        if mes is not None:
            consulta = consulta.filter(extract("month", data) == mes)

        if semana is not None:
            limites = {
                1: (1, 7),
                2: (8, 14),
                3: (15, 21),
                4: (22, 31),
            }

            inicio, fim = limites[semana]
            dia = extract("day", data)

            consulta = consulta.filter(
                dia >= inicio,
                dia <= fim,
            )

        if tipo != "Todas":
            consulta = consulta.filter(Indicacao.tipo_indicacao == tipo)

        return consulta

    def consultar_relatorio_area(self):
        ano, mes, semana, tipo = self.obter_filtros_relatorio()
        session = SessionLocal()

        try:
            areas = session.query(Area).order_by(Area.nome).all()
            resultados = []

            limites = {
                1: (1, 7),
                2: (8, 14),
                3: (15, 21),
                4: (22, 31),
            }

            for area in areas:
                nome_area = (area.nome or "").strip().casefold()

                if "projet" in nome_area:
                    consulta = session.query(
                        func.coalesce(func.max(Processo.quantidade), 0)
                    ).filter(Processo.area_id == area.id)

                    if ano is not None:
                        consulta = consulta.filter(
                            extract("year", Processo.data_processo) == ano
                        )

                    if mes is not None:
                        consulta = consulta.filter(
                            extract("month", Processo.data_processo) == mes
                        )

                    if semana is not None:
                        inicio, fim = limites[semana]
                        dia = extract("day", Processo.data_processo)

                        consulta = consulta.filter(
                            dia >= inicio,
                            dia <= fim,
                        )

                    total_processos = (consulta.scalar() or 0) if tipo == "Todas" else 0

                    total_indicacoes = 0

                else:
                    consulta = session.query(Indicacao).filter(
                        Indicacao.area_id == area.id
                    )

                    consulta = self.aplicar_filtros_relatorio(
                        consulta,
                        ano=ano,
                        mes=mes,
                        semana=semana,
                        tipo=tipo,
                    )

                    total_indicacoes = consulta.count()

                    total_processos = (
                        consulta.with_entities(
                            func.coalesce(func.max(Indicacao.quantidade), 0)
                        ).scalar()
                        or 0
                    )

                resultados.append(
                    (
                        area.nome,
                        int(total_processos),
                        total_indicacoes,
                    )
                )

            total_geral_processos = sum(processos for _, processos, _ in resultados)

            return resultados, total_geral_processos

        finally:
            session.close()

    def atualizar_relatorio_area(self):
        if not hasattr(self, "linhas_relatorios"):
            return

        for widget in self.linhas_relatorios.winfo_children():
            widget.destroy()

        try:
            resultados, total_processos = self.consultar_relatorio_area()

            self.card_relatorio_processos.atualizar_valor(total_processos)

            total_areas_com_resultados = sum(
                1
                for _, processos, indicacoes in resultados
                if processos > 0 or indicacoes > 0
            )

            self.card_relatorio_areas.atualizar_valor(total_areas_com_resultados)

            if not resultados:
                Mensagem(
                    self.linhas_relatorios,
                    "Nenhum resultado encontrado para os filtros selecionados.",
                    tipo="alerta",
                ).pack(pady=30)
                return

            for indice, (area, processos, indicacoes) in enumerate(resultados):
                linha = ctk.CTkFrame(
                    self.linhas_relatorios,
                    fg_color=(
                        CORES["fundo_secundario"] if indice % 2 == 0 else CORES["card"]
                    ),
                    corner_radius=6,
                )
                linha.pack(fill="x", pady=3)

                for coluna in range(3):
                    linha.grid_columnconfigure(
                        coluna,
                        weight=3 if coluna == 0 else 1,
                    )

                valores = [
                    area,
                    str(processos),
                    str(indicacoes),
                ]

                for coluna, valor in enumerate(valores):
                    ctk.CTkLabel(
                        linha,
                        text=valor,
                        text_color=CORES["texto"],
                        font=ctk.CTkFont(
                            size=13,
                            weight=("bold" if coluna == 0 else "normal"),
                        ),
                        anchor="w" if coluna == 0 else "center",
                    ).grid(
                        row=0,
                        column=coluna,
                        padx=12,
                        pady=10,
                        sticky="ew",
                    )

        except Exception as erro:
            Mensagem(
                self.linhas_relatorios,
                f"Erro ao gerar o relatório:\n{erro}",
                tipo="erro",
            ).pack(pady=30)

    def exportar_relatorio_excel(self):
        try:
            resultados, total_processos = self.consultar_relatorio_area()

            if not resultados:
                messagebox.showwarning(
                    "Relatório vazio",
                    "Não existem dados para exportar com os filtros selecionados.",
                )
                return

            ano, mes, semana, tipo = self.obter_filtros_relatorio()

            caminho = filedialog.asksaveasfilename(
                title="Salvar relatório por área",
                defaultextension=".xlsx",
                filetypes=[("Planilha Excel", "*.xlsx")],
                initialfile="relatorio_por_area.xlsx",
            )

            if not caminho:
                return

            workbook = Workbook()
            planilha = workbook.active
            planilha.title = "Relatório por Área"

            planilha.append(
                [
                    "Área",
                    "Total de Processos",
                    "Total de Indicações",
                ]
            )

            for area, processos, indicacoes in resultados:
                planilha.append(
                    [
                        area,
                        processos,
                        indicacoes,
                    ]
                )

            for celula in planilha[1]:
                celula.font = Font(
                    bold=True,
                    color="FFFFFF",
                )
                celula.fill = PatternFill(
                    fill_type="solid",
                    fgColor="244062",
                )
                celula.alignment = Alignment(horizontal="center")

            planilha.column_dimensions["A"].width = 30
            planilha.column_dimensions["B"].width = 24
            planilha.column_dimensions["C"].width = 24

            planilha.append([])
            planilha.append(["Filtros aplicados"])
            planilha.append(
                [
                    "Ano",
                    ano if ano is not None else "Todos",
                ]
            )
            planilha.append(
                [
                    "Mês",
                    self.combo_mes_relatorios.get(),
                ]
            )
            planilha.append(
                [
                    "Semana",
                    self.combo_semana_relatorios.get(),
                ]
            )
            planilha.append(
                [
                    "Tipo de indicação",
                    tipo,
                ]
            )
            planilha.append(
                [
                    "Total geral de processos",
                    total_processos,
                ]
            )

            workbook.save(caminho)

            messagebox.showinfo(
                "Exportação concluída",
                f"Relatório salvo com sucesso em:\n\n{caminho}",
            )

        except Exception as erro:
            messagebox.showerror(
                "Erro na exportação",
                f"Não foi possível exportar o relatório:\n\n{erro}",
            )
