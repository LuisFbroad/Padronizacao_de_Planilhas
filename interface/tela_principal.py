import customtkinter as ctk
import pandas as pd

from tkinter import filedialog, messagebox

from interface.tema import CORES
from interface.componentes import CardIndicador, BotaoPrincipal, TituloSecao, Mensagem

from src.excel.leitor import LeitorExcel
from src.excel.padronizador import PadronizadorExcel
from src.excel.validador import ValidadorExcel
from src.services.indicadores import IndicadoresService


class TelaPrincipal(ctk.CTkFrame):

    TIPOS_INDICACAO = ["Primária", "Secundária", "Terciária", "Quaternária", "Final"]

    def __init__(self, master, **kwargs):

        super().__init__(master, fg_color=CORES["fundo"], **kwargs)

        # ==========================================================
        # VARIÁVEIS
        # ==========================================================

        self.dados = pd.DataFrame()

        self.leitor = None
        self.indicadores_service = None

        self.modo_todas_indicacoes = False

        self.tela_atual = None

        # ==========================================================
        # CONSTRUÇÃO
        # ==========================================================

        self.criar_interface()

        self.mostrar_dashboard()

    # ==============================================================
    # INTERFACE PRINCIPAL
    # ==============================================================

    def criar_interface(self):

        # ----------------------------------------------------------
        # SIDEBAR
        # ----------------------------------------------------------

        self.sidebar = ctk.CTkFrame(
            self, width=220, fg_color=CORES["sidebar"], corner_radius=0
        )

        self.sidebar.pack(side="left", fill="y")

        self.sidebar.pack_propagate(False)

        # ----------------------------------------------------------
        # LOGO / NOME
        # ----------------------------------------------------------

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

        # ----------------------------------------------------------
        # MENU
        # ----------------------------------------------------------

        self.criar_botao_menu("Dashboard", self.mostrar_dashboard)

        self.criar_botao_menu("Planilha", self.mostrar_planilha)

        self.criar_botao_menu("Indicadores", self.mostrar_indicadores)

        self.criar_botao_menu("Relatórios", self.mostrar_relatorios)

        # ----------------------------------------------------------
        # ESPAÇO
        # ----------------------------------------------------------

        self.espaco_sidebar = ctk.CTkFrame(self.sidebar, fg_color="transparent")

        self.espaco_sidebar.pack(fill="both", expand=True)

        # ----------------------------------------------------------
        # BOTÃO CARREGAR EXCEL
        # ----------------------------------------------------------

        self.botao_carregar = ctk.CTkButton(
            self.sidebar,
            text="＋  Carregar Excel",
            command=self.carregar_excel,
            height=42,
            corner_radius=8,
            fg_color=CORES["destaque"],
            hover_color=CORES["destaque_hover"],
            text_color="#FFFFFF",
            font=ctk.CTkFont(size=13, weight="bold"),
        )

        self.botao_carregar.pack(padx=18, pady=(10, 30), fill="x")

        # ----------------------------------------------------------
        # ÁREA PRINCIPAL
        # ----------------------------------------------------------

        self.area_principal = ctk.CTkFrame(
            self, fg_color=CORES["fundo"], corner_radius=0
        )

        self.area_principal.pack(side="left", fill="both", expand=True)

    # ==============================================================
    # BOTÕES DA SIDEBAR
    # ==============================================================

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

    # ==============================================================
    # LIMPAR ÁREA PRINCIPAL
    # ==============================================================

    def limpar_area(self):

        for widget in self.area_principal.winfo_children():
            widget.destroy()

    # ==============================================================
    # TÍTULO
    # ==============================================================

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

    # ==============================================================
    # DASHBOARD
    # ==============================================================

    def mostrar_dashboard(self):

        self.tela_atual = "dashboard"

        self.limpar_area()

        self.criar_cabecalho("Dashboard", "Visão geral das informações da planilha")

        # ----------------------------------------------------------
        # CARDS
        # ----------------------------------------------------------

        cards = ctk.CTkFrame(self.area_principal, fg_color="transparent")

        cards.pack(fill="x", padx=30, pady=(10, 20))

        cards.grid_columnconfigure(0, weight=1)

        cards.grid_columnconfigure(1, weight=1)

        self.card_processos = CardIndicador(
            cards, titulo="Processos", valor=self.quantidade_processos(), icone="▣"
        )

        self.card_processos.grid(row=0, column=0, padx=(0, 10), sticky="ew")

        self.card_indicadores = CardIndicador(
            cards, titulo="Indicadores", valor="0", icone="◆"
        )

        self.card_indicadores.grid(row=0, column=1, padx=(10, 0), sticky="ew")

        # ----------------------------------------------------------
        # FILTRO
        # ----------------------------------------------------------

        filtro_container = ctk.CTkFrame(
            self.area_principal,
            fg_color=CORES["card"],
            corner_radius=12,
            border_width=1,
            border_color=CORES["borda"],
        )

        filtro_container.pack(fill="x", padx=30, pady=(0, 15))

        titulo_filtro = ctk.CTkLabel(
            filtro_container,
            text="Filtro de indicações",
            text_color=CORES["texto"],
            font=ctk.CTkFont(size=15, weight="bold"),
        )

        titulo_filtro.pack(anchor="w", padx=20, pady=(15, 8))

        filtro_frame = ctk.CTkFrame(filtro_container, fg_color="transparent")

        filtro_frame.pack(fill="x", padx=20, pady=(0, 15))

        # ----------------------------------------------------------
        # COMBO
        # ----------------------------------------------------------

        self.combo_dashboard_tipo = ctk.CTkComboBox(
            filtro_frame,
            values=self.TIPOS_INDICACAO,
            width=190,
            height=36,
            command=self.atualizar_ranking_dashboard,
        )

        self.combo_dashboard_tipo.set("Primária")

        self.combo_dashboard_tipo.pack(side="left", padx=(0, 10))

        # ----------------------------------------------------------
        # BOTÃO TODAS
        # ----------------------------------------------------------

        self.botao_todas_indicacoes = ctk.CTkButton(
            filtro_frame,
            text="Todas as indicações",
            command=self.mostrar_todas_indicacoes,
            width=190,
            height=36,
            corner_radius=8,
            fg_color=CORES["destaque"],
            hover_color=CORES["destaque_hover"],
            text_color="#FFFFFF",
            font=ctk.CTkFont(size=12, weight="bold"),
        )

        self.botao_todas_indicacoes.pack(side="left", padx=(0, 10))

        # ----------------------------------------------------------
        # BOTÃO VOLTAR
        # ----------------------------------------------------------

        self.botao_voltar_tipos = ctk.CTkButton(
            filtro_frame,
            text="Voltar aos tipos",
            command=self.voltar_tipos_indicacao,
            width=160,
            height=36,
            corner_radius=8,
            fg_color=CORES["sidebar"],
            hover_color=CORES["sidebar_hover"],
            text_color="#FFFFFF",
            font=ctk.CTkFont(size=12, weight="bold"),
        )

        # IMPORTANTE:
        # O botão começa escondido.
        # Ele só aparece quando "Todas" estiver ativo.

        # ----------------------------------------------------------
        # RANKING
        # ----------------------------------------------------------

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

        # ----------------------------------------------------------
        # ÁREA DE RANKING COM SCROLL
        # ----------------------------------------------------------

        self.ranking_scroll = ctk.CTkScrollableFrame(
            ranking_container, fg_color="transparent"
        )

        self.ranking_scroll.pack(fill="both", expand=True, padx=15, pady=(0, 15))

        self.atualizar_ranking_dashboard()

    # ==============================================================
    # MOSTRAR TODAS AS INDICAÇÕES
    # ==============================================================

    def mostrar_todas_indicacoes(self):

        self.modo_todas_indicacoes = True

        # ----------------------------------------------------------
        # DESATIVA O COMBO
        # ----------------------------------------------------------

        self.combo_dashboard_tipo.configure(state="disabled")

        # ----------------------------------------------------------
        # DESATIVA O PRÓPRIO BOTÃO
        # ----------------------------------------------------------

        self.botao_todas_indicacoes.configure(
            text="✓ Todas as indicações",
            state="disabled",
            fg_color="#555555",
            hover_color="#555555",
        )

        # ----------------------------------------------------------
        # MOSTRA BOTÃO VOLTAR
        # ----------------------------------------------------------

        self.botao_voltar_tipos.pack(side="left")

        # ----------------------------------------------------------
        # ATUALIZA RANKING
        # ----------------------------------------------------------

        self.atualizar_ranking_dashboard()

    # ==============================================================
    # VOLTAR PARA OS TIPOS
    # ==============================================================

    def voltar_tipos_indicacao(self):

        self.modo_todas_indicacoes = False

        # ----------------------------------------------------------
        # ATIVA COMBO
        # ----------------------------------------------------------

        self.combo_dashboard_tipo.configure(state="normal")

        self.combo_dashboard_tipo.set("Primária")

        # ----------------------------------------------------------
        # ATIVA BOTÃO TODAS
        # ----------------------------------------------------------

        self.botao_todas_indicacoes.configure(
            text="Todas as indicações",
            state="normal",
            fg_color=CORES["destaque"],
            hover_color=CORES["destaque_hover"],
        )

        # ----------------------------------------------------------
        # ESCONDE BOTÃO VOLTAR
        # ----------------------------------------------------------

        self.botao_voltar_tipos.pack_forget()

        # ----------------------------------------------------------
        # ATUALIZA
        # ----------------------------------------------------------

        self.atualizar_ranking_dashboard()

    # ==============================================================
    # ATUALIZAR RANKING
    # ==============================================================

    def atualizar_ranking_dashboard(self, tipo=None):

        if not hasattr(self, "ranking_scroll"):
            return

        # ----------------------------------------------------------
        # LIMPA RANKING
        # ----------------------------------------------------------

        for widget in self.ranking_scroll.winfo_children():
            widget.destroy()

        # ----------------------------------------------------------
        # VERIFICA SE EXISTE DADO
        # ----------------------------------------------------------

        if self.indicadores_service is None:

            self.card_indicadores.atualizar(0)

            mensagem = Mensagem(
                self.ranking_scroll,
                "Carregue uma planilha Excel para visualizar os indicadores.",
                tipo="alerta",
            )

            mensagem.pack(pady=30)

            return

        # ----------------------------------------------------------
        # MODO TODAS
        # ----------------------------------------------------------

        if self.modo_todas_indicacoes:

            try:

                ranking = self.indicadores_service.contar_todas_indicacoes()

            except Exception as erro:

                Mensagem(
                    self.ranking_scroll,
                    f"Erro ao calcular indicadores: {erro}",
                    tipo="erro",
                ).pack(pady=30)

                return

        # ----------------------------------------------------------
        # MODO TIPO ESPECÍFICO
        # ----------------------------------------------------------

        else:

            tipo_selecionado = tipo if tipo else self.combo_dashboard_tipo.get()

            try:

                ranking = self.indicadores_service.contar_indicacoes(tipo_selecionado)

            except Exception as erro:

                Mensagem(
                    self.ranking_scroll,
                    f"Erro ao calcular indicadores: {erro}",
                    tipo="erro",
                ).pack(pady=30)

                return

        # ----------------------------------------------------------
        # ATUALIZA CARD
        # ----------------------------------------------------------

        quantidade_indicadores = len(ranking)

        self.card_indicadores.atualizar(quantidade_indicadores)

        # ----------------------------------------------------------
        # SEM RESULTADOS
        # ----------------------------------------------------------

        if ranking.empty:

            Mensagem(
                self.ranking_scroll, "Nenhuma indicação encontrada.", tipo="alerta"
            ).pack(pady=30)

            return

        # ----------------------------------------------------------
        # MOSTRA RANKING
        # ----------------------------------------------------------

        self.mostrar_ranking(ranking)

    # ==============================================================
    # MOSTRAR RANKING
    # ==============================================================

    def mostrar_ranking(self, ranking):

        for indice, linha in ranking.iterrows():

            indicador = linha["indicador"]
            quantidade = int(linha["quantidade"])

            numero = indice + 1

            # ------------------------------------------------------
            # CARD DO RANKING
            # ------------------------------------------------------

            linha_frame = ctk.CTkFrame(
                self.ranking_scroll,
                fg_color=CORES["fundo_secundario"],
                corner_radius=8,
                border_width=1,
                border_color=CORES["borda"],
            )

            linha_frame.pack(fill="x", pady=4, padx=3)

            # ------------------------------------------------------
            # POSIÇÃO
            # ------------------------------------------------------

            posicao = ctk.CTkLabel(
                linha_frame,
                text=f"{numero}º",
                width=55,
                text_color=CORES["destaque"],
                font=ctk.CTkFont(size=14, weight="bold"),
            )

            posicao.pack(side="left", padx=(10, 5))

            # ------------------------------------------------------
            # NOME
            # ------------------------------------------------------

            nome = ctk.CTkLabel(
                linha_frame,
                text=str(indicador),
                text_color=CORES["texto"],
                font=ctk.CTkFont(size=14, weight="bold"),
                anchor="w",
            )

            nome.pack(side="left", fill="x", expand=True, padx=10)

            # ------------------------------------------------------
            # QUANTIDADE
            # ------------------------------------------------------

            texto_quantidade = (
                "pessoa indicada" if quantidade == 1 else "pessoas indicadas"
            )

            quantidade_label = ctk.CTkLabel(
                linha_frame,
                text=f"{quantidade} {texto_quantidade}",
                text_color=CORES["texto_secundario"],
                font=ctk.CTkFont(size=13),
            )

            quantidade_label.pack(side="right", padx=15)

    # ==============================================================
    # PLANILHA
    # ==============================================================

    def mostrar_planilha(self):

        self.tela_atual = "planilha"

        self.limpar_area()

        self.criar_cabecalho("Planilha", "Visualização dos dados carregados")

        # ----------------------------------------------------------
        # SEM PLANILHA
        # ----------------------------------------------------------

        if self.dados.empty:

            Mensagem(
                self.area_principal, "Nenhuma planilha foi carregada.", tipo="alerta"
            ).pack(pady=50)

            return

        # ----------------------------------------------------------
        # CONTAINER
        # ----------------------------------------------------------

        container = ctk.CTkFrame(
            self.area_principal,
            fg_color=CORES["card"],
            corner_radius=12,
            border_width=1,
            border_color=CORES["borda"],
        )

        container.pack(fill="both", expand=True, padx=30, pady=(0, 30))

        # ----------------------------------------------------------
        # INFORMAÇÕES
        # ----------------------------------------------------------

        info = ctk.CTkLabel(
            container,
            text=(
                f"Registros: {len(self.dados)}    "
                f"Colunas: {len(self.dados.columns)}"
            ),
            text_color=CORES["texto_secundario"],
            font=ctk.CTkFont(size=13),
        )

        info.pack(anchor="w", padx=20, pady=15)

        # ----------------------------------------------------------
        # TABELA SIMPLES
        # ----------------------------------------------------------

        tabela = ctk.CTkScrollableFrame(container, fg_color="transparent")

        tabela.pack(fill="both", expand=True, padx=15, pady=(0, 15))

        # Cabeçalho
        for coluna_numero, coluna in enumerate(self.dados.columns):

            label = ctk.CTkLabel(
                tabela,
                text=str(coluna),
                text_color=CORES["texto_claro"],
                fg_color=CORES["sidebar"],
                corner_radius=5,
                width=150,
                height=35,
                font=ctk.CTkFont(size=12, weight="bold"),
            )

            label.grid(row=0, column=coluna_numero, padx=2, pady=2, sticky="nsew")

        # Dados
        limite = min(len(self.dados), 200)

        for linha_numero in range(limite):

            for coluna_numero, coluna in enumerate(self.dados.columns):

                valor = self.dados.iloc[linha_numero, coluna_numero]

                if pd.isna(valor):
                    valor = ""

                label = ctk.CTkLabel(
                    tabela,
                    text=str(valor),
                    text_color=CORES["texto"],
                    fg_color=CORES["fundo_secundario"],
                    corner_radius=4,
                    width=150,
                    height=32,
                    anchor="w",
                )

                label.grid(
                    row=linha_numero + 1,
                    column=coluna_numero,
                    padx=2,
                    pady=2,
                    sticky="nsew",
                )

    # ==============================================================
    # INDICADORES
    # ==============================================================

    def mostrar_indicadores(self):

        self.tela_atual = "indicadores"

        self.limpar_area()

        self.criar_cabecalho("Indicadores", "Análise das indicações cadastradas")

        # ----------------------------------------------------------
        # SEM DADOS
        # ----------------------------------------------------------

        if self.indicadores_service is None:

            Mensagem(
                self.area_principal,
                "Carregue uma planilha para visualizar os indicadores.",
                tipo="alerta",
            ).pack(pady=50)

            return

        # ----------------------------------------------------------
        # FILTRO
        # ----------------------------------------------------------

        filtro = ctk.CTkFrame(
            self.area_principal,
            fg_color=CORES["card"],
            corner_radius=12,
            border_width=1,
            border_color=CORES["borda"],
        )

        filtro.pack(fill="x", padx=30, pady=(0, 15))

        titulo = ctk.CTkLabel(
            filtro,
            text="Tipo de indicação",
            text_color=CORES["texto"],
            font=ctk.CTkFont(size=14, weight="bold"),
        )

        titulo.pack(anchor="w", padx=20, pady=(15, 8))

        combo = ctk.CTkComboBox(
            filtro,
            values=self.TIPOS_INDICACAO,
            width=200,
            command=self.atualizar_tela_indicadores,
        )

        combo.set("Primária")

        combo.pack(anchor="w", padx=20, pady=(0, 15))

        self.combo_indicadores = combo

        # ----------------------------------------------------------
        # RANKING
        # ----------------------------------------------------------

        self.area_indicadores = ctk.CTkScrollableFrame(
            self.area_principal, fg_color=CORES["card"], corner_radius=12
        )

        self.area_indicadores.pack(fill="both", expand=True, padx=30, pady=(0, 30))

        self.atualizar_tela_indicadores("Primária")

    # ==============================================================
    # ATUALIZAR INDICADORES
    # ==============================================================

    def atualizar_tela_indicadores(self, tipo=None):

        if not hasattr(self, "area_indicadores"):
            return

        for widget in self.area_indicadores.winfo_children():
            widget.destroy()

        tipo = tipo if tipo else self.combo_indicadores.get()

        try:

            ranking = self.indicadores_service.contar_indicacoes(tipo)

        except Exception as erro:

            Mensagem(self.area_indicadores, f"Erro: {erro}", tipo="erro").pack(pady=30)

            return

        if ranking.empty:

            Mensagem(
                self.area_indicadores, "Nenhuma indicação encontrada.", tipo="alerta"
            ).pack(pady=30)

            return

        for indice, linha in ranking.iterrows():

            indicador = linha["indicador"]

            quantidade = int(linha["quantidade"])

            frame = ctk.CTkFrame(
                self.area_indicadores,
                fg_color=CORES["fundo_secundario"],
                corner_radius=8,
                border_width=1,
                border_color=CORES["borda"],
            )

            frame.pack(fill="x", padx=5, pady=4)

            posicao = ctk.CTkLabel(
                frame,
                text=f"{indice + 1}º",
                width=60,
                text_color=CORES["destaque"],
                font=ctk.CTkFont(size=14, weight="bold"),
            )

            posicao.pack(side="left", padx=10)

            nome = ctk.CTkLabel(
                frame,
                text=str(indicador),
                text_color=CORES["texto"],
                font=ctk.CTkFont(size=14, weight="bold"),
            )

            nome.pack(side="left", fill="x", expand=True, anchor="w")

            quantidade_label = ctk.CTkLabel(
                frame,
                text=str(quantidade),
                text_color=CORES["texto_secundario"],
                font=ctk.CTkFont(size=14, weight="bold"),
            )

            quantidade_label.pack(side="right", padx=20)

    # ==============================================================
    # RELATÓRIOS
    # ==============================================================

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

    # ==============================================================
    # CARREGAR EXCEL
    # ==============================================================

    def carregar_excel(self):

        caminho = filedialog.askopenfilename(
            title="Selecionar planilha Excel",
            filetypes=[
                ("Arquivos Excel", "*.xlsx *.xlsm *.xls"),
                ("Todos os arquivos", "*.*"),
            ],
        )

        if not caminho:
            return

        try:

            # ------------------------------------------------------
            # LEITOR
            # ------------------------------------------------------

            self.leitor = LeitorExcel(caminho)

            # ------------------------------------------------------
            # ABA PRINCIPAL
            # ------------------------------------------------------

            nome_aba = "RELATÓRIO MENSAL (NOVOS)"

            abas = self.leitor.listar_abas()

            if nome_aba not in abas:

                raise ValueError(
                    f"A aba '{nome_aba}' "
                    "não foi encontrada.\n\n"
                    f"Abas encontradas: {abas}"
                )

            # ------------------------------------------------------
            # LEITURA
            # ------------------------------------------------------

            dados = self.leitor.ler_aba(nome_aba, linha_cabecalho=3)

            # ------------------------------------------------------
            # PADRONIZAÇÃO
            # ------------------------------------------------------

            padronizador = PadronizadorExcel()

            dados = padronizador.padronizar(dados)

            # ------------------------------------------------------
            # VALIDAÇÃO
            # ------------------------------------------------------

            validador = ValidadorExcel()

            erros = validador.validar_colunas(dados)

            if erros:

                mensagem = "A planilha possui problemas:\n\n" + "\n".join(erros)

                messagebox.showwarning("Aviso", mensagem)

            # ------------------------------------------------------
            # SALVA DADOS
            # ------------------------------------------------------

            self.dados = dados

            # ------------------------------------------------------
            # SERVICE
            # ------------------------------------------------------

            self.indicadores_service = IndicadoresService(self.dados)

            # ------------------------------------------------------
            # ATUALIZA PROCESSOS
            # ------------------------------------------------------

            if hasattr(self, "card_processos"):

                self.card_processos.atualizar(self.quantidade_processos())

            # ------------------------------------------------------
            # RESET DO MODO TODAS
            # ------------------------------------------------------

            self.modo_todas_indicacoes = False

            # ------------------------------------------------------
            # DASHBOARD
            # ------------------------------------------------------

            self.mostrar_dashboard()

            messagebox.showinfo("Sucesso", "Planilha carregada com sucesso!")

        except Exception as erro:

            messagebox.showerror("Erro ao carregar planilha", str(erro))

    # ==============================================================
    # QUANTIDADE DE PROCESSOS
    # ==============================================================

    def quantidade_processos(self):

        if self.dados.empty:
            return 0

        # ----------------------------------------------------------
        # TENTA USAR NÚMERO DO PROCESSO
        # ----------------------------------------------------------

        colunas_processo = ["numero_processo", "Nº do Processo", "NÚMERO DO PROCESSO"]

        for coluna in colunas_processo:

            if coluna in self.dados.columns:

                valores = self.dados[coluna].dropna().astype(str).str.strip()

                valores = valores[valores != ""]

                return len(valores)

        # ----------------------------------------------------------
        # CASO NÃO EXISTA NÚMERO DO PROCESSO
        # ----------------------------------------------------------

        return len(self.dados)
