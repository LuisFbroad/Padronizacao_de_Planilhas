import customtkinter as ctk

from interface.tela_principal import TelaPrincipal


def iniciar_aplicacao():

    ctk.set_appearance_mode("dark")
    ctk.set_default_color_theme("blue")

    app = ctk.CTk()

    app.title("Sistema GAGC")

    app.geometry("1200x700")

    app.minsize(1000, 600)

    tela = TelaPrincipal(app)

    tela.pack(fill="both", expand=True)

    app.mainloop()


if __name__ == "__main__":
    iniciar_aplicacao()
