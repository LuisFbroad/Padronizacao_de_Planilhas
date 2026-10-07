from sqlalchemy.orm import Session
from src.database.models import Pessoa, Indicacao


def buscar_ou_criar_pessoa(session: Session, nome: str):
    pessoa = session.query(Pessoa).filter(Pessoa.nome == nome).first()

    if pessoa is None:
        pessoa = Pessoa(nome=nome)
        session.add(pessoa)
        session.flush()

    return pessoa


def registrar_indicacao(session: Session, nome: str):
    pessoa = buscar_ou_criar_pessoa(session, nome)

    indicacao = Indicacao(pessoa_id=pessoa.id)

    session.add(indicacao)


def contar_indicacoes(session: Session, nome: str):
    pessoa = session.query(Pessoa).filter(Pessoa.nome == nome).first()

    if pessoa is None:
        return 0

    return session.query(Indicacao).filter(Indicacao.pessoa_id == pessoa.id).count()
