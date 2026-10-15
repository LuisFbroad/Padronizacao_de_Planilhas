from pathlib import Path
from datetime import date, datetime
import re
import unicodedata

import pandas as pd
from sqlalchemy import func
from sqlalchemy.dialects.postgresql import insert as pg_insert

from src.database.connection import SessionLocal
from src.database.models import Area, Pessoa, Indicacao, Processo

PASTA_DADOS = Path("__Agosto_Padrão__")


COLUNAS_INDICACAO = {
    "INDICACAO PRIMARIA": "Primária",
    "INDICACAO SECUNDARIA": "Secundária",
    "INDICACAO TERCIARIA": "Terciária",
    "INDICACAO QUARTERNARIA": "Quaternária",
    "INDICACAO QUATERNARIA": "Quaternária",
    "INDICACAO FINAL": "Final",
}


AREAS_ARQUIVOS = {
    "CIV": {
        "nome": "Civil",
        "alternativas": ["Civil", "Cível"],
    },
    "PREV": {
        "nome": "Previdencia",
        "alternativas": [
            "Previdencia",
            "Previdência",
            "Previdenciário",
            "Previdenciária",
        ],
    },
    "PROJ": {
        "nome": "Projeto",
        "alternativas": ["Projeto", "Projetos"],
    },
    "REV": {
        "nome": "Restituição",
        "alternativas": ["Restituição", "Restituicao", "Revisão", "Revisao"],
    },
    "TRAB": {
        "nome": "Trabalhista",
        "alternativas": ["Trabalhista"],
    },
}


def normalizar_texto(valor):
    if valor is None:
        return ""

    texto = str(valor).strip()

    texto = unicodedata.normalize("NFKD", texto)
    texto = "".join(
        caractere for caractere in texto if not unicodedata.combining(caractere)
    )

    texto = texto.upper()
    texto = re.sub(r"[^A-Z0-9]+", " ", texto)

    return " ".join(texto.split())


def normalizar_nome(nome):
    if nome is None or pd.isna(nome):
        return ""

    return " ".join(str(nome).strip().split())


def limpar_valor(valor):
    if valor is None:
        return None

    try:
        if pd.isna(valor):
            return None
    except (TypeError, ValueError):
        pass

    if isinstance(valor, float) and valor.is_integer():
        valor = int(valor)

    texto = str(valor).strip()

    if not texto or texto.lower() in {"nan", "none", "null"}:
        return None

    return texto


def normalizar_coluna(coluna):
    return normalizar_texto(coluna)


def preparar_linha(linha):
    dados = {}

    for coluna, valor in linha.items():
        chave = normalizar_coluna(coluna)

        if chave:
            dados[chave] = valor

    return dados


def obter_campo(dados, alternativas):
    for alternativa in alternativas:
        chave = normalizar_coluna(alternativa)

        if chave in dados:
            valor = limpar_valor(dados[chave])

            if valor is not None:
                return valor

    return None


def identificar_area(nome_arquivo):
    nome = nome_arquivo.upper()

    for sigla, configuracao in AREAS_ARQUIVOS.items():
        if f"_{sigla}_" in nome:
            return configuracao

    return None


def buscar_area(session, configuracao):
    alternativas = configuracao["alternativas"]

    nomes_normalizados = {normalizar_texto(nome) for nome in alternativas}

    areas = session.query(Area).all()

    for area in areas:
        if normalizar_texto(area.nome) in nomes_normalizados:
            return area

    area = Area(nome=configuracao["nome"])
    session.add(area)
    session.flush()

    return area


def buscar_ou_criar_pessoa(session, nome):
    nome = normalizar_nome(nome)

    if not nome:
        return None

    nome_normalizado = normalizar_texto(nome)

    if not nome_normalizado:
        return None

    # Primeiro verifica pessoas que já estão pendentes
    # de gravação nesta sessão.
    for objeto in session.new:
        if isinstance(objeto, Pessoa):
            if normalizar_texto(objeto.nome) == nome_normalizado:
                return objeto

    # Pesquisa sem provocar flush automático de outros objetos.
    with session.no_autoflush:
        pessoa = (
            session.query(Pessoa)
            .filter(func.upper(func.trim(Pessoa.nome)) == nome.upper().strip())
            .first()
        )

    if pessoa:
        return pessoa

    # O PostgreSQL ignora o INSERT se o nome exato já existir.
    # Isso evita a violação da restrição pessoas_nome_key.
    comando = (
        pg_insert(Pessoa)
        .values(nome=nome)
        .on_conflict_do_nothing(index_elements=[Pessoa.nome])
    )

    session.execute(comando)

    # Busca novamente o registro, inclusive se ele já existia.
    with session.no_autoflush:
        pessoa = (
            session.query(Pessoa)
            .filter(func.upper(func.trim(Pessoa.nome)) == nome.upper().strip())
            .first()
        )

    if pessoa:
        return pessoa

    # Caso tenha ocorrido uma concorrência ou uma variação
    # inesperada no registro, informa o problema sem esconder
    # o erro original do banco.
    raise RuntimeError(f"Não foi possível localizar ou cadastrar a pessoa: {nome}")


def obter_processo(dados):
    return obter_campo(
        dados,
        [
            "N do Processo",
            "Nº do Processo",
            "N° do Processo",
            "Numero do Processo",
            "Número do Processo",
            "Processo",
            "PRC/RPV",
        ],
    )


def obter_numero_rpv(dados):
    return obter_campo(
        dados,
        [
            "PRC/RPV",
            "N do Processo",
            "Nº do Processo",
            "N° do Processo",
            "Numero do Processo",
            "Número do Processo",
            "Processo",
        ],
    )


def obter_data(dados):
    valor = obter_campo(
        dados,
        [
            "Data",
            "Data do Processo",
            "Data da Indicação",
        ],
    )

    if not valor:
        return None

    try:
        data_convertida = pd.to_datetime(
            valor,
            dayfirst=True,
            errors="coerce",
        )

        if pd.isna(data_convertida):
            return None

        return data_convertida.date()

    except (TypeError, ValueError):
        return None


def obter_indicacoes(dados):
    indicacoes = []

    for coluna, tipo in COLUNAS_INDICACAO.items():
        valor = obter_campo(dados, [coluna])

        if not valor:
            continue

        # As planilhas podem separar várias pessoas por "/".
        partes = str(valor).split("/")

        for parte in partes:
            nome = normalizar_nome(parte)

            if not nome:
                continue

            if normalizar_texto(nome) in {
                "NAN",
                "NONE",
                "NULL",
                "N A",
            }:
                continue

            indicacoes.append(
                {
                    "nome": nome,
                    "tipo": tipo,
                }
            )

    return indicacoes


def buscar_ou_criar_processo(
    session,
    area,
    numero,
    data_processo,
    nome_arquivo,
    chaves_processos_pendentes,
):
    numero = limpar_valor(numero)

    if not numero:
        return False

    chave = (
        area.id,
        normalizar_texto(numero),
    )

    if chave in chaves_processos_pendentes:
        return False

    processo_existente = (
        session.query(Processo)
        .filter(
            Processo.area_id == area.id,
            Processo.numero == numero,
        )
        .first()
    )

    if processo_existente:
        chaves_processos_pendentes.add(chave)
        return False

    processo = Processo(
        area_id=area.id,
        numero=numero,
        data_processo=data_processo,
        arquivo_origem=nome_arquivo,
    )

    session.add(processo)
    session.flush()

    chaves_processos_pendentes.add(chave)

    return True


def indicacao_existe(
    session,
    pessoa_id,
    area_id,
    processo,
    tipo,
    data_indicacao,
    nome_arquivo,
):
    consulta = session.query(Indicacao).filter(
        Indicacao.pessoa_id == pessoa_id,
        Indicacao.area_id == area_id,
        Indicacao.tipo_indicacao == tipo,
    )

    if processo:
        consulta = consulta.filter(Indicacao.processo == processo)
    else:
        consulta = consulta.filter(
            Indicacao.processo.is_(None),
            Indicacao.arquivo_origem == nome_arquivo,
        )

        if data_indicacao:
            consulta = consulta.filter(Indicacao.data_indicacao == data_indicacao)
        else:
            consulta = consulta.filter(Indicacao.data_indicacao.is_(None))

    return consulta.first() is not None


def importar_planilha(
    caminho,
    session,
    chaves_indicacoes_pendentes,
    chaves_processos_pendentes,
):
    nome_arquivo = caminho.name
    configuracao = identificar_area(nome_arquivo)

    if not configuracao:
        print(f"[AVISO] Área não identificada: {nome_arquivo}")
        return 0, 0

    area = buscar_area(session, configuracao)

    print()
    print("=" * 80)
    print(f"ARQUIVO: {nome_arquivo}")
    print(f"ÁREA IDENTIFICADA: {area.nome}")
    print("=" * 80)

    df = pd.read_excel(caminho, header=3)

    total_indicacoes = 0
    total_processos = 0
    total_linhas_com_indicacao = 0

    eh_projeto = "PROJ" in nome_arquivo.upper()
    eh_trabalhista = "TRAB" in nome_arquivo.upper()

    for _, linha in df.iterrows():
        dados = preparar_linha(linha)

        numero_processo = obter_processo(dados)
        numero_rpv = obter_numero_rpv(dados)
        data_processo = obter_data(dados)
        indicacoes = obter_indicacoes(dados)

        # PROJETO:
        # importa os processos/RPVs mesmo sem indicadores.
        if eh_projeto and numero_rpv:
            inserido = buscar_ou_criar_processo(
                session=session,
                area=area,
                numero=numero_rpv,
                data_processo=data_processo,
                nome_arquivo=nome_arquivo,
                chaves_processos_pendentes=chaves_processos_pendentes,
            )

            if inserido:
                total_processos += 1

        # Se não há nomes de indicadores, não cria pessoas
        # nem indicações fictícias.
        if not indicacoes:
            continue

        total_linhas_com_indicacao += 1

        # TRABALHISTA:
        # importa as indicações das pessoas mesmo quando
        # a planilha não possui número de processo.
        if eh_trabalhista:
            processo_indicacao = numero_processo
        else:
            processo_indicacao = numero_processo

            # As demais áreas só geram indicações quando
            # há um processo associado.
            if not processo_indicacao:
                continue

        for item in indicacoes:
            nome = item["nome"]
            tipo = item["tipo"]

            pessoa = buscar_ou_criar_pessoa(session, nome)

            if pessoa is None:
                continue

            chave = (
                pessoa.id,
                area.id,
                processo_indicacao,
                tipo,
                data_processo if not processo_indicacao else None,
                nome_arquivo if not processo_indicacao else None,
            )

            # Impede duplicidade na própria execução,
            # inclusive para indicações sem processo.
            if chave in chaves_indicacoes_pendentes:
                continue

            if indicacao_existe(
                session=session,
                pessoa_id=pessoa.id,
                area_id=area.id,
                processo=processo_indicacao,
                tipo=tipo,
                data_indicacao=data_processo,
                nome_arquivo=nome_arquivo,
            ):
                chaves_indicacoes_pendentes.add(chave)
                continue

            indicacao = Indicacao(
                pessoa_id=pessoa.id,
                area_id=area.id,
                processo=processo_indicacao,
                tipo_indicacao=tipo,
                data_indicacao=data_processo,
                arquivo_origem=nome_arquivo,
            )

            session.add(indicacao)
            chaves_indicacoes_pendentes.add(chave)
            total_indicacoes += 1

    print(f"Linhas com indicação: {total_linhas_com_indicacao}")
    print(f"Processos/RPVs novos: {total_processos}")
    print(f"Indicações novas: {total_indicacoes}")

    return total_indicacoes, total_processos


def importar_todas():
    if not PASTA_DADOS.exists():
        print(f"[ERRO] Pasta não encontrada: {PASTA_DADOS.resolve()}")
        return

    arquivos = sorted(
        arquivo
        for arquivo in PASTA_DADOS.glob("*.xlsx")
        if not arquivo.name.startswith("~$")
    )

    if not arquivos:
        print(f"Nenhuma planilha encontrada em: {PASTA_DADOS.resolve()}")
        return

    session = SessionLocal()

    total_geral_indicacoes = 0
    total_geral_processos = 0

    chaves_indicacoes_pendentes = set()
    chaves_processos_pendentes = set()

    try:
        print("=" * 80)
        print("IMPORTAÇÃO DAS PLANILHAS")
        print("=" * 80)
        print(f"Planilhas encontradas: {len(arquivos)}")

        for arquivo in arquivos:
            novas_indicacoes, novos_processos = importar_planilha(
                caminho=arquivo,
                session=session,
                chaves_indicacoes_pendentes=chaves_indicacoes_pendentes,
                chaves_processos_pendentes=chaves_processos_pendentes,
            )

            total_geral_indicacoes += novas_indicacoes
            total_geral_processos += novos_processos

        session.commit()

        print()
        print("=" * 80)
        print("IMPORTAÇÃO CONCLUÍDA")
        print("=" * 80)
        print(f"Total de indicações inseridas: {total_geral_indicacoes}")
        print(f"Total de processos/RPVs inseridos: {total_geral_processos}")

    except Exception as erro:
        session.rollback()

        print()
        print("=" * 80)
        print("[ERRO] A importação foi cancelada.")
        print("=" * 80)
        print(f"Detalhes: {erro}")

        raise

    finally:
        session.close()


if __name__ == "__main__":
    importar_todas()
