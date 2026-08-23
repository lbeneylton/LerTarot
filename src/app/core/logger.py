import logging
from logging.handlers import RotatingFileHandler
from pathlib import Path


class AppLogger:
    LOG_DIR = Path("logs")
    LOG_FILE = LOG_DIR / "app.log"

    LOG_FORMAT = (
        "[%(asctime)s] "
        "%(levelname)s "
        "%(filename)s:%(lineno)d "
        "- %(message)s"
    )

    DATE_FORMAT = "%d-%m-%Y %H:%M:%S"

    def __init__(
        self,
        environment: str,
        name: str = "app"
    ) -> None:

        self.environment = environment
        self.name = name
        self.logger = logging.getLogger(name)

        if not self.logger.handlers:
            self._configure()

    def _configure(self) -> None:
        
        if not self.environment:
            raise ValueError("Ambiente não configurado")

        formatter = logging.Formatter(
            self.LOG_FORMAT,
            datefmt=self.DATE_FORMAT
        )

        # ==========================
        # DEV
        # ==========================

        if self.environment.upper() == "DEV":

            self.LOG_DIR.mkdir(exist_ok=True)

            self.logger.setLevel(logging.DEBUG)

            file_handler = RotatingFileHandler(
                self.LOG_FILE,
                maxBytes=5 * 1024 * 1024,
                backupCount=3,
                encoding="utf-8"
            )

            file_handler.setFormatter(formatter)
            self.logger.addHandler(file_handler)

        # ==========================
        # PROD
        # ==========================

        elif self.environment.upper() == "PROD":

            self.logger.setLevel(logging.INFO)
        else:
            raise ValueError("Ambiente desconhecido")

        # ==========================
        # CONSOLE
        # ==========================

        console_handler = logging.StreamHandler()
        console_handler.setFormatter(formatter)

        self.logger.addHandler(console_handler)
        

    def debug(self, message: str) -> None:
        self.logger.debug(message, stacklevel=2)

    def info(self, message: str) -> None:
        self.logger.info(message, stacklevel=2)

    def warning(
        self,
        message: str,
        *,
        exc_info=None
    ) -> None:

        self.logger.warning(
            message,
            stacklevel=2,
            exc_info=exc_info
        )

    def error(
        self,
        message: str,
        *,
        exc_info=None
    ) -> None:

        self.logger.error(
            message,
            stacklevel=2,
            exc_info=exc_info
        )

    def critical(
        self,
        message: str,
        *,
        exc_info=None
    ) -> None:

        self.logger.critical(
            message,
            stacklevel=2,
            exc_info=exc_info
        )

    def exception(self, message: str) -> None:
        self.logger.exception(
            message,
            stacklevel=2
        )