import customtkinter as ctk

from interface.tela_principal import TelaPrincipal
from interface.tema import configurar_tema


def iniciar_aplicacao():
    """
    Inicia a aplicação principal.
    """

    # Configura o tema fixo
    configurar_tema()

    # Cria a janela principal
    app = ctk.CTk()

    app.title("Sistema GAGC")

    app.geometry("1200x700")

    app.minsize(1000, 600)

    # Cria a tela principal
    tela = TelaPrincipal(app)

    tela.pack(fill="both", expand=True)

    # Inicia o sistema
    app.mainloop()


if __name__ == "__main__":
    iniciar_aplicacao()
