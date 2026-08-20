"""Handler das exceções do app"""
from fastapi import Request
from fastapi.responses import JSONResponse

# Importação da Exceção Base
from app.core.exceptions import AppException

# Para Logger
from app.core.logger import AppLogger
from app.core.config import get_settings

# Criando logger com o nome do arquivo
logger = AppLogger(
    get_settings().env,
    __name__
)


# Handler customizado para a exception AppException
async def app_exception_handler(
    request: Request,
    exc: AppException
):
    logger.warning(
        f"{exc.code} - {exc.message}",
        exc_info=exc
    )

    return JSONResponse(
        status_code=exc.status_code,
        content={
            "success": False,
            "error": {
                "code": exc.code,
                "message": exc.message
            }
        }
    )