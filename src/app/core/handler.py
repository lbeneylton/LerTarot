"""Handler das exceções do app"""
import logging

from fastapi import Request
from fastapi.responses import JSONResponse

# Importação da Exceção Base
from app.core.exceptions import AppException

# Criando logger com o nome do arquivo
logger = logging.getLogger(__name__)


# Handler customizado para a exception AppException
async def app_exception_handler(request: Request, exc: AppException):
    logger.warning(f"{exc.code} - {exc.message}")

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
