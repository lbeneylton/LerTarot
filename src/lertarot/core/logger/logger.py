import os
import logging
from logging.handlers import RotatingFileHandler


class Logger:
    """Wrapper padrão para logs do sistema"""

    def __init__(
        self,
        name: str = "log",
        log_dir: str = "logs",
        log_file: str = "log"
    ):
        self.logger = logging.getLogger(name)
        self.logger.setLevel(logging.INFO)

        # evita duplicar handlers
        if self.logger.handlers:
            return

        # cria pasta de logs se não existir
        os.makedirs(log_dir, exist_ok=True)

        log_path = os.path.join(log_dir, log_file)

        formatter = logging.Formatter(
            "[%(asctime)s] %(levelname)s - %(name)s - %(message)s",
            datefmt="%H:%M:%S"  # <-- só hora:minuto:segundo
        )

        # console handler
        console_handler = logging.StreamHandler()
        console_handler.setFormatter(formatter)

        # file handler com rotação
        file_handler = RotatingFileHandler(
            log_path,
            maxBytes=5 * 1024 * 1024,  # 5MB
            backupCount=3
        )
        file_handler.setFormatter(formatter)

        # adiciona handlers
        self.logger.addHandler(console_handler)
        self.logger.addHandler(file_handler)

    def info(self, message: str, **kwargs):
        self.logger.info(message, extra=kwargs)

    def error(self, message: str, **kwargs):
        self.logger.error(message, extra=kwargs)

    def warning(self, message: str, **kwargs):
        self.logger.warning(message, extra=kwargs)

    def debug(self, message: str, **kwargs):
        self.logger.debug(message, extra=kwargs)


logger = Logger()
