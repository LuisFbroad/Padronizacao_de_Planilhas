import customtkinter as ctk
from interface.tela_principal import TelaPrincipal
from src.services.importador import importar_todas


def main():
    print("=" * 60)
    print("SISTEMA DE INDICAÇÕES")
    print("Atualizando informações das planilhas...")
    print("=" * 60)

    try:
        importar_todas()
    except Exception as erro:
        print(f"Erro ao atualizar as planilhas: {erro}")
        input("Pressione Enter para sair...")
        return

    print("Atualização concluída. Abrindo o sistema...")

    app = ctk.CTk()
    app.title("Sistema de Indicações")
    app.geometry("1200x750")

    tela = TelaPrincipal(app)
    tela.pack(fill="both", expand=True)

    app.mainloop()


if __name__ == "__main__":
    main()
