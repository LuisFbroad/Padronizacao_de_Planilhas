import logging
from pathlib import Path

# Pasta onde os logs serão armazenados
PASTA_LOGS = Path("logs")

# Cria a pasta caso ela não exista
PASTA_LOGS.mkdir(parents=True, exist_ok=True)


# Arquivo de log
ARQUIVO_LOG = PASTA_LOGS / "sistema.log"


def configurar_logger():
    """
    Configura o sistema de logs.
    """

    logger = logging.getLogger("sistema_planilhas")

    # Evita criar vários logs duplicados
    if logger.handlers:
        return logger

    logger.setLevel(logging.INFO)

    # Formato das mensagens
    formato = logging.Formatter(
        "%(asctime)s | %(levelname)s | %(message)s", datefmt="%d/%m/%Y %H:%M:%S"
    )

    # ==========================================
    # LOG NO ARQUIVO
    # ==========================================

    arquivo = logging.FileHandler(ARQUIVO_LOG, encoding="utf-8")

    arquivo.setLevel(logging.INFO)
    arquivo.setFormatter(formato)

    logger.addHandler(arquivo)

    # ==========================================
    # LOG NO TERMINAL
    # ==========================================

    console = logging.StreamHandler()

    console.setLevel(logging.INFO)
    console.setFormatter(formato)

    logger.addHandler(console)

    return logger
