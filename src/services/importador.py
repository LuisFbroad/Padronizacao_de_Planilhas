import pandas as pd

from src.database.connection import SessionLocal
from src.database.repository import registrar_indicacao


def importar_planilha(caminho: str, coluna_nome: str):
    df = pd.read_excel(caminho)

    session = SessionLocal()

    try:
        for _, linha in df.iterrows():
            nome = linha[coluna_nome]

            if pd.isna(nome):
                continue

            nome = str(nome).strip()

            if not nome:
                continue

            registrar_indicacao(session, nome)

        session.commit()

    except Exception:
        session.rollback()
        raise

    finally:
        session.close()
