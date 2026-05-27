import logging
from logging.handlers import RotatingFileHandler
from pathlib import Path


# Diretorio para logs (cria se não existe)
LOG_DIR = Path("logs")
LOG_DIR.mkdir(exist_ok=True)

# Formato padrão dos logs   [DATA HORA] TIPO NOME_LOGGER MENSAGEM
LOG_FORMAT = (
    "[%(asctime)s] "
    "%(levelname)s "
    "%(name)s "
    "- %(message)s"
)

# Formata da data
DATE_FORMAT = "%d-%m-%Y %H:%M:%S"

# Formatador
formatter = logging.Formatter(
    LOG_FORMAT,
    datefmt=DATE_FORMAT
)

# Handler de arquivos
file_handler = RotatingFileHandler(
    LOG_DIR / "app.log",
    maxBytes=5 * 1024 * 1024,  # (5 MB)
    backupCount=3,
    encoding="utf-8"
)

# Setando o formato de arquivo para o file_handler
file_handler.setFormatter(formatter)

# Logs no console
console_handler = logging.StreamHandler()
console_handler.setFormatter(formatter)

# configurações dos LOGS, onde serão exibidos e nivel minimo (INFO)
logging.basicConfig(
    level=logging.DEBUG,
    handlers=[
        console_handler,
        file_handler
    ]
)

if __name__ == "__main__":
    # Criação da instâcia do logger
    logger = logging.getLogger("app")
    logger.error("Pix enviado")
