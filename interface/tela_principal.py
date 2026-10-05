import customtkinter as ctk
from tkinter import filedialog, messagebox
from pathlib import Path

from src.excel.leitor import LeitorExcel
from src.excel.padronizador import PadronizadorExcel
from src.services.indicadores import IndicadoresService
from src.logger import configurar_logger


class TelaPrincipal(ctk.CTkFrame):

    def __init__(self, master):

        super().__init__(master)

        # ==========================================
        # CONFIGURAÇÕES
        # ==========================================

        self.master = master

        self.logger = configurar_logger()

        self.caminho_arquivo = None
        self.leitor = None
        self.dados = None
        self.abas = []

        self.indicadores = None

        self.criar_interface()

    # ==========================================
    # CRIAR INTERFACE
    # ==========================================

    def criar_interface(self):

        # ==========================================
        # CABEÇALHO
        # ==========================================

        self.titulo = ctk.CTkLabel(
            self, text="Sistema GAGC", font=ctk.CTkFont(size=28, weight="bold")
        )

        self.titulo.pack(pady=(25, 5))

        self.subtitulo = ctk.CTkLabel(
            self, text="Gestão e consulta de planilhas", font=ctk.CTkFont(size=14)
        )

        self.subtitulo.pack(pady=(0, 20))

        # ==========================================
        # ÁREA PRINCIPAL
        # ==========================================

        self.conteudo = ctk.CTkFrame(self, corner_radius=15)

        self.conteudo.pack(fill="both", expand=True, padx=30, pady=10)

        # ==========================================
        # ARQUIVO
        # ==========================================

        self.label_arquivo = ctk.CTkLabel(
            self.conteudo,
            text="Arquivo Excel",
            font=ctk.CTkFont(size=18, weight="bold"),
        )

        self.label_arquivo.pack(pady=(20, 5))

        self.nome_arquivo = ctk.CTkLabel(
            self.conteudo, text="Nenhum arquivo selecionado", font=ctk.CTkFont(size=14)
        )

        self.nome_arquivo.pack(pady=(0, 10))

        self.botao_carregar = ctk.CTkButton(
            self.conteudo,
            text="📂 Carregar Excel",
            height=40,
            width=220,
            command=self.carregar_excel,
        )

        self.botao_carregar.pack(pady=(0, 20))

        # ==========================================
        # CARDS
        # ==========================================

        self.cards = ctk.CTkFrame(self.conteudo, fg_color="transparent")

        self.cards.pack(fill="x", padx=30)

        self.card_abas = self.criar_card(self.cards, "Abas", "0", 0)

        self.card_registros = self.criar_card(self.cards, "Registros", "0", 1)

        self.card_colunas = self.criar_card(self.cards, "Colunas", "0", 2)

        # ==========================================
        # ÁREA DE INDICADORES
        # ==========================================

        self.criar_area_indicadores()

    # ==========================================
    # CRIAR CARD
    # ==========================================

    def criar_card(self, parent, titulo, valor, coluna):

        card = ctk.CTkFrame(parent, corner_radius=12)

        card.grid(row=0, column=coluna, padx=10, pady=10, sticky="nsew")

        parent.grid_columnconfigure(coluna, weight=1)

        label_titulo = ctk.CTkLabel(card, text=titulo, font=ctk.CTkFont(size=13))

        label_titulo.pack(pady=(12, 3))

        label_valor = ctk.CTkLabel(
            card, text=valor, font=ctk.CTkFont(size=26, weight="bold")
        )

        label_valor.pack(pady=(0, 12))

        return label_valor

    # ==========================================
    # ÁREA DE INDICADORES
    # ==========================================

    def criar_area_indicadores(self):

        self.frame_indicadores = ctk.CTkFrame(self.conteudo, corner_radius=12)

        self.frame_indicadores.pack(fill="both", expand=True, padx=30, pady=(20, 20))

        # ==========================================
        # TÍTULO
        # ==========================================

        self.titulo_indicadores = ctk.CTkLabel(
            self.frame_indicadores,
            text="🔎 Indicadores",
            font=ctk.CTkFont(size=20, weight="bold"),
        )

        self.titulo_indicadores.pack(pady=(20, 10))

        # ==========================================
        # SELETOR DO TIPO
        # ==========================================

        self.frame_filtro = ctk.CTkFrame(self.frame_indicadores, fg_color="transparent")

        self.frame_filtro.pack(fill="x", padx=30, pady=(0, 10))

        self.label_tipo = ctk.CTkLabel(self.frame_filtro, text="Tipo de indicação:")

        self.label_tipo.pack(side="left", padx=(0, 10))

        self.tipo_indicacao = ctk.CTkComboBox(
            self.frame_filtro,
            values=["Primária", "Secundária", "Terciária", "Quaternária", "Final"],
            width=200,
            command=self.atualizar_indicadores,
        )

        self.tipo_indicacao.set("Primária")

        self.tipo_indicacao.pack(side="left")

        # ==========================================
        # CABEÇALHO DA LISTA
        # ==========================================

        self.frame_cabecalho = ctk.CTkFrame(
            self.frame_indicadores, fg_color="transparent"
        )

        self.frame_cabecalho.pack(fill="x", padx=30, pady=(10, 0))

        self.label_nome_coluna = ctk.CTkLabel(
            self.frame_cabecalho,
            text="Indicador",
            font=ctk.CTkFont(size=14, weight="bold"),
            anchor="w",
        )

        self.label_nome_coluna.pack(side="left", fill="x", expand=True)

        self.label_quantidade_coluna = ctk.CTkLabel(
            self.frame_cabecalho,
            text="Indicações",
            font=ctk.CTkFont(size=14, weight="bold"),
            width=120,
        )

        self.label_quantidade_coluna.pack(side="right")

        # ==========================================
        # LISTA DE RESULTADOS
        # ==========================================

        self.resultado = ctk.CTkScrollableFrame(self.frame_indicadores, corner_radius=8)

        self.resultado.pack(fill="both", expand=True, padx=30, pady=(5, 20))

        # ==========================================
        # MENSAGEM INICIAL
        # ==========================================

        self.label_inicial = ctk.CTkLabel(
            self.resultado,
            text="Carregue um Excel para visualizar os indicadores.",
            font=ctk.CTkFont(size=14),
        )

        self.label_inicial.pack(pady=30)

    # ==========================================
    # CARREGAR EXCEL
    # ==========================================

    def carregar_excel(self):

        self.logger.info("Usuário solicitou carregamento de Excel")

        caminho = filedialog.askopenfilename(
            title="Selecionar planilha Excel",
            filetypes=[
                ("Arquivos Excel", "*.xlsx *.xlsm *.xls"),
                ("Excel XLSX", "*.xlsx"),
                ("Excel XLSM", "*.xlsm"),
                ("Excel XLS", "*.xls"),
            ],
        )

        # ==========================================
        # CANCELAMENTO
        # ==========================================

        if not caminho:

            self.logger.info("Seleção de arquivo cancelada")

            return

        try:

            # ======================================
            # LEITOR
            # ======================================

            self.leitor = LeitorExcel(caminho)

            self.caminho_arquivo = Path(caminho)

            # ======================================
            # LISTAR ABAS
            # ======================================

            self.abas = self.leitor.listar_abas()

            if not self.abas:

                raise ValueError("O arquivo não possui abas.")

            # ======================================
            # LER PRIMEIRA ABA
            # ======================================

            primeira_aba = self.abas[0]

            self.logger.info(f"Lendo aba: {primeira_aba}")

            dados = self.leitor.ler_aba(primeira_aba)

            # ======================================
            # PADRONIZAR
            # ======================================

            padronizador = PadronizadorExcel()

            self.dados = padronizador.padronizar(dados)

            # ======================================
            # CRIAR SERVIÇO DE INDICADORES
            # ======================================

            self.indicadores = IndicadoresService(self.dados)

            # ======================================
            # ATUALIZAR NOME DO ARQUIVO
            # ======================================

            self.nome_arquivo.configure(text=self.caminho_arquivo.name)

            # ======================================
            # ATUALIZAR CARDS
            # ======================================

            self.card_abas.configure(text=str(len(self.abas)))

            self.card_registros.configure(text=str(len(self.dados)))

            self.card_colunas.configure(text=str(len(self.dados.columns)))

            # ======================================
            # ATUALIZAR INDICADORES
            # ======================================

            self.atualizar_indicadores()

            # ======================================
            # LOG
            # ======================================

            self.logger.info(
                f"Excel carregado com sucesso: " f"{self.caminho_arquivo.name}"
            )

            self.logger.info(f"Registros encontrados: " f"{len(self.dados)}")

            self.logger.info(f"Colunas encontradas: " f"{len(self.dados.columns)}")

            # ======================================
            # MENSAGEM
            # ======================================

            messagebox.showinfo(
                "Excel carregado",
                (
                    "Planilha carregada com sucesso!\n\n"
                    f"Arquivo: {self.caminho_arquivo.name}\n"
                    f"Abas: {len(self.abas)}\n"
                    f"Registros: {len(self.dados)}"
                ),
            )

        except Exception as erro:

            self.logger.exception(f"Erro ao carregar Excel: {erro}")

            messagebox.showerror(
                "Erro", ("Não foi possível carregar " "a planilha.\n\n" f"Erro: {erro}")
            )

    # ==========================================
    # ATUALIZAR INDICADORES
    # ==========================================

    def atualizar_indicadores(self, escolha=None):

        # ==========================================
        # VERIFICAR SE EXISTE DADO
        # ==========================================

        if self.indicadores is None:

            return

        try:

            # ======================================
            # TIPO SELECIONADO
            # ======================================

            tipo = self.tipo_indicacao.get()

            self.logger.info(f"Atualizando indicadores: {tipo}")

            # ======================================
            # CALCULAR INDICADORES
            # ======================================

            resultado = self.indicadores.contar_indicacoes(tipo)

            # ======================================
            # LIMPAR RESULTADOS
            # ======================================

            for widget in self.resultado.winfo_children():

                widget.destroy()

            # ======================================
            # NENHUM RESULTADO
            # ======================================

            if resultado.empty:

                mensagem = ctk.CTkLabel(
                    self.resultado,
                    text=("Nenhuma indicação encontrada " f"em '{tipo}'."),
                    font=ctk.CTkFont(size=14),
                )

                mensagem.pack(pady=30)

                return

            # ======================================
            # CRIAR LINHAS
            # ======================================

            for _, linha in resultado.iterrows():

                indicador = linha["indicador"]

                quantidade = int(linha["quantidade"])

                self.criar_linha_indicador(indicador, quantidade)

            # ======================================
            # LOG
            # ======================================

            self.logger.info(
                f"{len(resultado)} indicadores " f"encontrados para {tipo}"
            )

        except Exception as erro:

            self.logger.exception(f"Erro ao atualizar indicadores: {erro}")

            messagebox.showerror(
                "Erro", ("Não foi possível carregar " "os indicadores.\n\n" f"{erro}")
            )

    # ==========================================
    # CRIAR LINHA DO INDICADOR
    # ==========================================

    def criar_linha_indicador(self, indicador, quantidade):

        linha = ctk.CTkFrame(self.resultado, corner_radius=8)

        linha.pack(fill="x", pady=4, padx=5)

        # ==========================================
        # NOME
        # ==========================================

        label_nome = ctk.CTkLabel(
            linha, text=str(indicador), font=ctk.CTkFont(size=14), anchor="w"
        )

        label_nome.pack(side="left", fill="x", expand=True, padx=15, pady=10)

        # ==========================================
        # QUANTIDADE
        # ==========================================

        texto_quantidade = "1 pessoa" if quantidade == 1 else f"{quantidade} pessoas"

        label_quantidade = ctk.CTkLabel(
            linha,
            text=texto_quantidade,
            font=ctk.CTkFont(size=14, weight="bold"),
            width=120,
        )

        label_quantidade.pack(side="right", padx=15, pady=10)
