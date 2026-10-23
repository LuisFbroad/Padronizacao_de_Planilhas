from sqlalchemy import func, extract

from src.database.connection import SessionLocal
from src.database.models import Area, Pessoa, Indicacao

# =========================================================
# FILTROS DE PERÍODO
# =========================================================


def aplicar_filtros_periodo(
    consulta,
    ano=None,
    mes=None,
    semana=None,
):
    data = Indicacao.data_indicacao

    # Datas nulas ficam naturalmente fora dos filtros de período.
    if ano is not None:
        consulta = consulta.filter(extract("year", data) == int(ano))

    if mes is not None:
        consulta = consulta.filter(extract("month", data) == int(mes))

    if semana is not None:
        limites = {
            1: (1, 7),
            2: (8, 14),
            3: (15, 21),
            4: (22, 31),
        }

        inicio, fim = limites[int(semana)]
        dia = extract("day", data)

        consulta = consulta.filter(
            dia >= inicio,
            dia <= fim,
        )

    return consulta


def aplicar_filtro_tipo(consulta, tipo_indicacao=None):
    if tipo_indicacao and tipo_indicacao != "Todas":
        consulta = consulta.filter(Indicacao.tipo_indicacao == tipo_indicacao)

    return consulta


# =========================================================
# ÁREAS
# =========================================================


def listar_areas():
    session = SessionLocal()

    try:
        return session.query(Area).order_by(Area.nome).all()
    finally:
        session.close()


def listar_areas_com_indicacoes(
    ano=None,
    mes=None,
    semana=None,
    tipo_indicacao=None,
):
    session = SessionLocal()

    try:
        # Inclui indicações com e sem número de processo.
        consulta = session.query(Area).join(
            Indicacao,
            Indicacao.area_id == Area.id,
        )

        consulta = aplicar_filtros_periodo(
            consulta,
            ano=ano,
            mes=mes,
            semana=semana,
        )

        consulta = aplicar_filtro_tipo(
            consulta,
            tipo_indicacao,
        )

        return consulta.distinct().order_by(Area.nome).all()
    finally:
        session.close()


# =========================================================
# PESSOAS
# =========================================================


def listar_pessoas_por_area(area_id):
    session = SessionLocal()

    try:
        # Pessoas com indicações sem processo também são listadas.
        return (
            session.query(Pessoa)
            .join(
                Indicacao,
                Indicacao.pessoa_id == Pessoa.id,
            )
            .filter(
                Indicacao.area_id == area_id,
            )
            .distinct()
            .order_by(Pessoa.nome)
            .all()
        )
    finally:
        session.close()


# =========================================================
# ANOS E SEMANAS DISPONÍVEIS
# =========================================================


def listar_anos_disponiveis():
    session = SessionLocal()

    try:
        resultados = (
            session.query(
                extract(
                    "year",
                    Indicacao.data_indicacao,
                ).label("ano")
            )
            .filter(Indicacao.data_indicacao.isnot(None))
            .distinct()
            .order_by(
                extract(
                    "year",
                    Indicacao.data_indicacao,
                ).desc()
            )
            .all()
        )

        return [int(ano) for (ano,) in resultados if ano is not None]
    finally:
        session.close()


def listar_semanas_disponiveis(ano=None, mes=None):
    session = SessionLocal()

    try:
        consulta = session.query(
            extract(
                "day",
                Indicacao.data_indicacao,
            ).label("dia")
        ).filter(Indicacao.data_indicacao.isnot(None))

        if ano is not None:
            consulta = consulta.filter(
                extract(
                    "year",
                    Indicacao.data_indicacao,
                )
                == int(ano)
            )

        if mes is not None:
            consulta = consulta.filter(
                extract(
                    "month",
                    Indicacao.data_indicacao,
                )
                == int(mes)
            )

        dias = consulta.all()
        semanas = set()

        for (dia,) in dias:
            if dia is None:
                continue

            dia = int(dia)

            if dia <= 7:
                semanas.add(1)
            elif dia <= 14:
                semanas.add(2)
            elif dia <= 21:
                semanas.add(3)
            else:
                semanas.add(4)

        return sorted(semanas)

    finally:
        session.close()


# =========================================================
# PROCESSOS POR PESSOA
# =========================================================


def contar_processos_por_pessoa(
    pessoa_id,
    area_id,
    tipo_indicacao=None,
    ano=None,
    mes=None,
    semana=None,
):
    session = SessionLocal()

    try:
        # Processo sem identificação não é contado como processo.
        consulta = session.query(func.count(func.distinct(Indicacao.processo))).filter(
            Indicacao.pessoa_id == pessoa_id,
            Indicacao.area_id == area_id,
            Indicacao.processo.isnot(None),
        )

        consulta = aplicar_filtro_tipo(
            consulta,
            tipo_indicacao,
        )

        consulta = aplicar_filtros_periodo(
            consulta,
            ano=ano,
            mes=mes,
            semana=semana,
        )

        return consulta.scalar() or 0

    finally:
        session.close()


def listar_processos_por_pessoa(
    pessoa_id,
    area_id,
    tipo_indicacao=None,
    ano=None,
    mes=None,
    semana=None,
):
    session = SessionLocal()

    try:
        consulta = session.query(Indicacao.processo).filter(
            Indicacao.pessoa_id == pessoa_id,
            Indicacao.area_id == area_id,
            Indicacao.processo.isnot(None),
        )

        consulta = aplicar_filtro_tipo(
            consulta,
            tipo_indicacao,
        )

        consulta = aplicar_filtros_periodo(
            consulta,
            ano=ano,
            mes=mes,
            semana=semana,
        )

        resultados = consulta.distinct().order_by(Indicacao.processo).all()

        return [processo for (processo,) in resultados]

    finally:
        session.close()


# =========================================================
# RANKING
# =========================================================


def listar_ranking(
    area_id,
    tipo_indicacao=None,
    ano=None,
    mes=None,
    semana=None,
):
    session = SessionLocal()

    try:
        # Inclui pessoas com indicação sem processo.
        # O total_processos dessas pessoas pode ser zero.
        total_processos = func.count(func.distinct(Indicacao.processo)).label(
            "total_processos"
        )

        consulta = (
            session.query(
                Pessoa.nome,
                total_processos,
            )
            .join(
                Indicacao,
                Indicacao.pessoa_id == Pessoa.id,
            )
            .filter(
                Indicacao.area_id == area_id,
            )
        )

        consulta = aplicar_filtro_tipo(
            consulta,
            tipo_indicacao,
        )

        consulta = aplicar_filtros_periodo(
            consulta,
            ano=ano,
            mes=mes,
            semana=semana,
        )

        return (
            consulta.group_by(
                Pessoa.id,
                Pessoa.nome,
            )
            .order_by(
                func.count(func.distinct(Indicacao.processo)).desc(),
                Pessoa.nome,
            )
            .all()
        )

    finally:
        session.close()


# =========================================================
# TOTAL DE PROCESSOS
# =========================================================


def contar_total_processos(
    area_id=None,
    tipo_indicacao=None,
    ano=None,
    mes=None,
    semana=None,
):
    session = SessionLocal()

    try:
        consulta = session.query(func.count(func.distinct(Indicacao.processo))).filter(
            Indicacao.processo.isnot(None)
        )

        if area_id is not None:
            consulta = consulta.filter(Indicacao.area_id == area_id)

        consulta = aplicar_filtro_tipo(
            consulta,
            tipo_indicacao,
        )

        consulta = aplicar_filtros_periodo(
            consulta,
            ano=ano,
            mes=mes,
            semana=semana,
        )

        return consulta.scalar() or 0

    finally:
        session.close()


# =========================================================
# TOTAL DE PESSOAS
# =========================================================


def contar_total_pessoas(
    area_id=None,
    tipo_indicacao=None,
    ano=None,
    mes=None,
    semana=None,
):
    session = SessionLocal()

    try:
        # Conta pessoas com indicação, mesmo sem processo.
        consulta = session.query(func.count(func.distinct(Indicacao.pessoa_id))).filter(
            Indicacao.pessoa_id.isnot(None)
        )

        if area_id is not None:
            consulta = consulta.filter(Indicacao.area_id == area_id)

        consulta = aplicar_filtro_tipo(
            consulta,
            tipo_indicacao,
        )

        consulta = aplicar_filtros_periodo(
            consulta,
            ano=ano,
            mes=mes,
            semana=semana,
        )

        return consulta.scalar() or 0

    finally:
        session.close()


# =========================================================
# RELATÓRIO AGRUPADO POR ÁREA
# =========================================================


def listar_relatorio_por_area(
    ano=None,
    mes=None,
    semana=None,
    tipo_indicacao=None,
):
    session = SessionLocal()

    try:
        consulta = session.query(
            Area.id.label("area_id"),
            Area.nome.label("area"),
            func.count(func.distinct(Indicacao.processo)).label("total_processos"),
            func.count(Indicacao.id).label("total_indicacoes"),
        ).join(
            Indicacao,
            Indicacao.area_id == Area.id,
        )

        consulta = aplicar_filtro_tipo(
            consulta,
            tipo_indicacao,
        )

        consulta = aplicar_filtros_periodo(
            consulta,
            ano=ano,
            mes=mes,
            semana=semana,
        )

        return (
            consulta.group_by(
                Area.id,
                Area.nome,
            )
            .order_by(Area.nome)
            .all()
        )

    finally:
        session.close()


def contar_areas_com_resultados(
    ano=None,
    mes=None,
    semana=None,
    tipo_indicacao=None,
):
    session = SessionLocal()

    try:
        # Conta áreas com indicações, não apenas com processos.
        consulta = session.query(func.count(func.distinct(Indicacao.area_id))).filter(
            Indicacao.area_id.isnot(None)
        )

        consulta = aplicar_filtro_tipo(
            consulta,
            tipo_indicacao,
        )

        consulta = aplicar_filtros_periodo(
            consulta,
            ano=ano,
            mes=mes,
            semana=semana,
        )

        return consulta.scalar() or 0

    finally:
        session.close()
