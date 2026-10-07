from src.database.connection import engine, testar_conexao
from src.database.models import Base

if __name__ == "__main__":
    if testar_conexao():
        Base.metadata.create_all(engine)
        print("Tabelas verificadas com sucesso.")
