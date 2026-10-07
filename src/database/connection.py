import os

from dotenv import load_dotenv
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker

load_dotenv()

DB_HOST = os.getenv("DB_HOST")
DB_PORT = os.getenv("DB_PORT")
DB_NAME = os.getenv("DB_NAME")
DB_USER = os.getenv("DB_USER")
DB_PASSWORD = os.getenv("DB_PASSWORD")

DATABSE_URL = (
    f"postgresql+psycopg2://" f"{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
)

engine = create_engine(
    DATABSE_URL,
    pool_pre_ping=True
    
)

SessionLocal = sessionmaker(
    bind=engine,
    autocommit=False,
    autoflush=False
)

def testar_conexao():
    try:
        with engine.connect() as connection:
            connection.execute(text("SELECT 1"))

        print("Conexão com o banco estabelecida com sucesso.")
        return True

    except Exception as e:
        print(f"Erro ao tentar conectar com o banco. \n{e}")
        return False