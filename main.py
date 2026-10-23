
import traceback
from tkinter import messagebox


def main():
    try:
        # Abre a interface principal sem importar planilhas automaticamente.
        from interface.app import iniciar_aplicacao

        iniciar_aplicacao()

    except Exception as erro:
        traceback.print_exc()

        try:
            messagebox.showerror(
                "Erro ao iniciar o Sistema GAGC",
                (
                    "Não foi possível abrir a interface.\n\n"
                    f"Erro: {erro}\n\n"
                    "Consulte o terminal para ver os detalhes."
                ),
            )
        except Exception:
            pass


if __name__ == "__main__":
    main()
