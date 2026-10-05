import customtkinter as ctk
from tkinter import filedialog, messagebox
from pathlib import Path

from src.excel.leitor import LeitorExcel
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

        self.criar_interface()

    def criar_interface(self):

        # ==========================================
        # CABEÇALHO
        # ==========================================

        self.titulo = ctk.CTkLabel(
            self, text="Sistema GAGC", font=ctk.CTkFont(size=28, weight="bold")
        )

        self.titulo.pack(pady=(30, 5))

        self.subtitulo = ctk.CTkLabel(
            self, text="Gestão e consulta de planilhas", font=ctk.CTkFont(size=14)
        )

        self.subtitulo.pack(pady=(0, 25))

        # ==========================================
        # ÁREA PRINCIPAL
        # ==========================================

        self.conteudo = ctk.CTkFrame(self, corner_radius=15)

        self.conteudo.pack(fill="both", expand=True, padx=30, pady=10)

        # ==========================================
        # SEÇÃO ARQUIVO
        # ==========================================

        self.label_arquivo = ctk.CTkLabel(
            self.conteudo,
            text="Arquivo Excel",
            font=ctk.CTkFont(size=18, weight="bold"),
        )

        self.label_arquivo.pack(pady=(25, 10))

        self.nome_arquivo = ctk.CTkLabel(
            self.conteudo, text="Nenhum arquivo selecionado", font=ctk.CTkFont(size=14)
        )

        self.nome_arquivo.pack(pady=(0, 15))

        # ==========================================
        # BOTÃO CARREGAR
        # ==========================================

        self.botao_carregar = ctk.CTkButton(
            self.conteudo,
            text="📂 Carregar Excel",
            height=45,
            width=220,
            command=self.carregar_excel,
        )

        self.botao_carregar.pack(pady=(0, 30))

        # ==========================================
        # CARDS
        # ==========================================

        self.cards = ctk.CTkFrame(self.conteudo, fg_color="transparent")

        self.cards.pack(fill="x", padx=30)

        self.card_abas = self.criar_card(self.cards, "Abas", "0", 0)

        self.card_registros = self.criar_card(self.cards, "Registros", "0", 1)

        self.card_colunas = self.criar_card(self.cards, "Colunas", "0", 2)

        # ==========================================
        # ÁREA DE ABAS
        # ==========================================

        self.label_abas = ctk.CTkLabel(
            self.conteudo,
            text="Abas encontradas",
            font=ctk.CTkFont(size=18, weight="bold"),
        )

        self.label_abas.pack(pady=(30, 10))

        self.lista_abas = ctk.CTkTextbox(self.conteudo, height=120)

        self.lista_abas.pack(fill="x", padx=30, pady=(0, 25))

        self.lista_abas.insert("1.0", "Nenhum arquivo carregado.")

        self.lista_abas.configure(state="disabled")

    # ==========================================
    # CRIAR CARD
    # ==========================================

    def criar_card(self, parent, titulo, valor, coluna):

        card = ctk.CTkFrame(parent, corner_radius=12)

        card.grid(row=0, column=coluna, padx=10, pady=10, sticky="nsew")

        parent.grid_columnconfigure(coluna, weight=1)

        label_titulo = ctk.CTkLabel(card, text=titulo, font=ctk.CTkFont(size=13))

        label_titulo.pack(pady=(15, 5))

        label_valor = ctk.CTkLabel(
            card, text=valor, font=ctk.CTkFont(size=28, weight="bold")
        )

        label_valor.pack(pady=(0, 15))

        return label_valor

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
                ("Todos os arquivos", "*.*"),
            ],
        )

        # ==========================================
        # USUÁRIO CANCELou
        # ==========================================

        if not caminho:

            self.logger.info("Seleção de arquivo cancelada pelo usuário")

            return

        try:

            self.logger.info(f"Arquivo selecionado: {caminho}")

            # ==========================================
            # CRIAR LEITOR
            # ==========================================

            self.leitor = LeitorExcel(caminho)

            self.caminho_arquivo = Path(caminho)

            # ==========================================
            # LISTAR ABAS
            # ==========================================

            self.abas = self.leitor.listar_abas()

            self.logger.info(f"Abas encontradas: {self.abas}")

            # ==========================================
            # ATUALIZAR NOME DO ARQUIVO
            # ==========================================

            self.nome_arquivo.configure(text=self.caminho_arquivo.name)

            # ==========================================
            # LER PRIMEIRA ABA
            # ==========================================

            if not self.abas:

                raise ValueError("O arquivo não possui abas.")

            primeira_aba = self.abas[0]

            self.logger.info(f"Lendo primeira aba: {primeira_aba}")

            self.dados = self.leitor.ler_aba(primeira_aba)

            # ==========================================
            # ATUALIZAR CARDS
            # ==========================================

            quantidade_abas = len(self.abas)

            quantidade_registros = len(self.dados)

            quantidade_colunas = len(self.dados.columns)

            self.card_abas.configure(text=str(quantidade_abas))

            self.card_registros.configure(text=str(quantidade_registros))

            self.card_colunas.configure(text=str(quantidade_colunas))

            # ==========================================
            # MOSTRAR ABAS
            # ==========================================

            self.lista_abas.configure(state="normal")

            self.lista_abas.delete("1.0", "end")

            for aba in self.abas:

                self.lista_abas.insert("end", f"• {aba}\n")

            self.lista_abas.configure(state="disabled")

            # ==========================================
            # LOG
            # ==========================================

            self.logger.info(
                f"Excel carregado com sucesso: "
                f"{quantidade_registros} registros, "
                f"{quantidade_colunas} colunas"
            )

            # ==========================================
            # MENSAGEM
            # ==========================================

            messagebox.showinfo(
                "Excel carregado",
                (
                    "Planilha carregada com sucesso!\n\n"
                    f"Arquivo: {self.caminho_arquivo.name}\n"
                    f"Abas: {quantidade_abas}\n"
                    f"Registros: {quantidade_registros}\n"
                    f"Colunas: {quantidade_colunas}"
                ),
            )

        except Exception as erro:

            # ==========================================
            # LOG DO ERRO
            # ==========================================

            self.logger.exception(f"Erro ao carregar Excel: {erro}")

            # ==========================================
            # MENSAGEM DE ERRO
            # ==========================================

            messagebox.showerror(
                "Erro", ("Não foi possível carregar " "a planilha.\n\n" f"Erro: {erro}")
            )
