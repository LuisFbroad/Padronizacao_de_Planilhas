from __future__ import annotations

import os
import shutil
import subprocess
import sys
from datetime import datetime
from pathlib import Path

from sqlalchemy.engine import make_url


def _obter_raiz_projeto() -> Path:
    """Localiza a pasta principal do projeto ou do aplicativo empacotado."""
    if getattr(sys, "frozen", False):
        return Path(sys.executable).resolve().parent

    return Path(__file__).resolve().parents[2]


def _obter_pasta_backup() -> Path:
    """Permite personalizar a pasta por variável de ambiente."""
    configurada = os.getenv("BACKUP_DIR")

    if configurada:
        pasta = Path(configurada).expanduser()
        if not pasta.is_absolute():
            pasta = _obter_raiz_projeto() / pasta
    else:
        pasta = _obter_raiz_projeto() / "backups"

    pasta.mkdir(parents=True, exist_ok=True)
    return pasta


def _obter_executavel(nome: str) -> Path:
    """Localiza pg_dump.exe ou pg_restore.exe."""
    extensao = ".exe" if os.name == "nt" else ""
    arquivo = nome + extensao

    # Caminho configurável, útil no servidor central.
    pasta_bin = os.getenv("PG_BIN_DIR")
    if pasta_bin:
        candidato = Path(pasta_bin) / arquivo
        if candidato.is_file():
            return candidato

    # Caminhos comuns de instalação e empacotamento.
    raiz = _obter_raiz_projeto()
    candidatos = [
        raiz / "PSQL" / "bin" / arquivo,
        raiz / "postgresql" / "bin" / arquivo,
        Path(sys.executable).resolve().parent / "PSQL" / "bin" / arquivo,
    ]

    for candidato in candidatos:
        if candidato.is_file():
            return candidato

    encontrado = shutil.which(arquivo)
    if encontrado:
        return Path(encontrado)

    raise FileNotFoundError(
        f"{arquivo} não encontrado. Configure a variável PG_BIN_DIR."
    )


def _obter_configuracao_banco():
    """Lê os parâmetros da DATABASE_URL sem imprimir credenciais."""
    url_texto = os.getenv("DATABASE_URL")

    if not url_texto:
        raise RuntimeError("DATABASE_URL não encontrada. Verifique o arquivo .env.")

    url = make_url(url_texto)

    if url.get_backend_name() != "postgresql":
        raise RuntimeError("A conexão configurada não é PostgreSQL.")

    if not url.host or not url.database or not url.username:
        raise RuntimeError("A DATABASE_URL precisa informar host, banco e usuário.")

    return url


def criar_backup() -> Path:
    """
    Gera um backup PostgreSQL no formato customizado.
    A senha é transmitida ao processo por variável de ambiente,
    não por argumento visível na linha de comando.
    """
    url = _obter_configuracao_banco()
    executavel = _obter_executavel("pg_dump")
    pasta = _obter_pasta_backup()

    data = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    destino = pasta / f"{url.database}_{data}.dump"

    comando = [
        str(executavel),
        "--host",
        url.host,
        "--port",
        str(url.port or 5432),
        "--username",
        url.username,
        "--dbname",
        url.database,
        "--format",
        "custom",
        "--no-password",
        "--file",
        str(destino),
    ]

    ambiente = os.environ.copy()
    ambiente.pop("PGPASSWORD", None)
    ambiente.pop("PGPASSFILE", None)

    if url.password is not None:
        ambiente["PGPASSWORD"] = url.password

    # Suporta configurações adicionais, como sslmode, quando presentes.
    if url.query:
        for chave in ("sslmode", "sslcert", "sslkey", "sslrootcert"):
            valor = url.query.get(chave)
            if isinstance(valor, str):
                ambiente["PG" + chave.upper()] = valor

    try:
        resultado = subprocess.run(
            comando,
            env=ambiente,
            capture_output=True,
            text=True,
            timeout=3600,
            check=False,
        )

        if resultado.returncode != 0:
            detalhe = resultado.stderr.strip() or "Erro sem detalhes."
            raise RuntimeError(
                f"pg_dump falhou (código {resultado.returncode}): " f"{detalhe[:1200]}"
            )

        if not destino.is_file() or destino.stat().st_size == 0:
            raise RuntimeError(
                "O comando terminou, mas o arquivo de backup está vazio "
                "ou não foi criado."
            )

        validar_backup(destino)
        return destino

    except Exception:
        # Remove apenas o arquivo incompleto desta tentativa.
        if destino.exists():
            destino.unlink()
        raise


def validar_backup(arquivo: str | Path) -> bool:
    """Verifica se o pg_restore consegue ler o catálogo do backup."""
    caminho = Path(arquivo)

    if not caminho.is_file() or caminho.stat().st_size == 0:
        raise FileNotFoundError("Arquivo de backup inexistente ou vazio.")

    executavel = _obter_executavel("pg_restore")

    resultado = subprocess.run(
        [str(executavel), "--list", str(caminho)],
        capture_output=True,
        text=True,
        timeout=120,
        check=False,
    )

    if resultado.returncode != 0 or "Dump Version:" not in resultado.stdout:
        detalhe = resultado.stderr.strip() or "Formato de backup inválido."
        raise RuntimeError(f"Falha na validação: {detalhe[:1200]}")

    return True
