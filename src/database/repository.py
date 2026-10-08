from sqlalchemy import func

from src.database.connection import SessionLocal
from src.database.models import Area, Pessoa, Indicacao


def listar_areas():
    session = SessionLocal()

    try:
        return session.query(Area).order_by(Area.nome).all()

    finally:
        session.close()


def listar_pessoas_por_area(area_id):
    session = SessionLocal()

    try:
        return (
            session.query(Pessoa)
            .join(Indicacao, Indicacao.pessoa_id == Pessoa.id)
            .filter(Indicacao.area_id == area_id)
            .distinct()
            .order_by(Pessoa.nome)
            .all()
        )

    finally:
        session.close()


def contar_processos_por_pessoa(pessoa_id, area_id, tipo_indicacao=None):
    session = SessionLocal()

    try:

        consulta = session.query(func.count(func.distinct(Indicacao.processo))).filter(
            Indicacao.pessoa_id == pessoa_id,
            Indicacao.area_id == area_id,
            Indicacao.processo.isnot(None),
        )

        if tipo_indicacao and tipo_indicacao != "Todas":
            consulta = consulta.filter(Indicacao.tipo_indicacao == tipo_indicacao)

        return consulta.scalar() or 0

    finally:
        session.close()


def listar_processos_por_pessoa(pessoa_id, area_id, tipo_indicacao=None):
    session = SessionLocal()

    try:

        consulta = session.query(Indicacao.processo).filter(
            Indicacao.pessoa_id == pessoa_id,
            Indicacao.area_id == area_id,
            Indicacao.processo.isnot(None),
        )

        if tipo_indicacao and tipo_indicacao != "Todas":
            consulta = consulta.filter(Indicacao.tipo_indicacao == tipo_indicacao)

        resultados = consulta.distinct().order_by(Indicacao.processo).all()

        return [processo for (processo,) in resultados]

    finally:
        session.close()


def listar_ranking(area_id, tipo_indicacao=None):
    session = SessionLocal()

    try:

        consulta = (
            session.query(
                Pessoa.nome,
                func.count(func.distinct(Indicacao.processo)).label("total_processos"),
            )
            .join(Indicacao, Indicacao.pessoa_id == Pessoa.id)
            .filter(Indicacao.area_id == area_id, Indicacao.processo.isnot(None))
        )

        if tipo_indicacao and tipo_indicacao != "Todas":
            consulta = consulta.filter(Indicacao.tipo_indicacao == tipo_indicacao)

        resultados = (
            consulta.group_by(Pessoa.id, Pessoa.nome)
            .order_by(func.count(func.distinct(Indicacao.processo)).desc(), Pessoa.nome)
            .all()
        )

        return resultados

    finally:
        session.close()


def contar_total_processos(area_id=None, tipo_indicacao=None):
    session = SessionLocal()

    try:

        consulta = session.query(func.count(func.distinct(Indicacao.processo))).filter(
            Indicacao.processo.isnot(None)
        )

        if area_id is not None:
            consulta = consulta.filter(Indicacao.area_id == area_id)

        if tipo_indicacao and tipo_indicacao != "Todas":
            consulta = consulta.filter(Indicacao.tipo_indicacao == tipo_indicacao)

        return consulta.scalar() or 0

    finally:
        session.close()


def contar_total_pessoas(area_id=None, tipo_indicacao=None):
    session = SessionLocal()

    try:

        consulta = session.query(func.count(func.distinct(Indicacao.pessoa_id))).filter(
            Indicacao.pessoa_id.isnot(None)
        )

        if area_id is not None:
            consulta = consulta.filter(Indicacao.area_id == area_id)

        if tipo_indicacao and tipo_indicacao != "Todas":
            consulta = consulta.filter(Indicacao.tipo_indicacao == tipo_indicacao)

        return consulta.scalar() or 0

    finally:
        session.close()
