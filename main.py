import customtkinter as ctk

from interface.tela_principal import TelaPrincipal


def main():

    app = ctk.CTk()

    app.title("Sistema de Indicações")

    app.geometry("1200x750")

    app.minsize(1000, 650)

    tela_principal = TelaPrincipal(app)

    tela_principal.pack(fill="both", expand=True)

    app.mainloop()


if __name__ == "__main__":
    main()
