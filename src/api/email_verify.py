from fastapi import APIRouter, Depends, status

from app.domains.users.models import User
from app.domains.verify.schemas import VerifyEmailRequest
from app.domains.verify.services import VerifyEmailService
from app.api.dependencies import get_email_verificator, get_current_user

verify_router = APIRouter(prefix="/email-verification", tags=["Email Verification"])


@verify_router.post("/send", status_code=status.HTTP_200_OK)
async def send_verification_email(
    current_user: User = Depends(get_current_user),
    email_verificator: VerifyEmailService = Depends(get_email_verificator),
) -> dict:
    """Gera e envia o código de verificação para o e-mail do usuário em segundo plano (outbox)."""
    await email_verificator.send_code(current_user)

    return {
        "message": "Código de verificação enviado com sucesso."
    }


@verify_router.post("/verify", status_code=status.HTTP_200_OK)
async def verify_email(
    data: VerifyEmailRequest,
    current_user: User = Depends(get_current_user),
    email_verificator: VerifyEmailService = Depends(get_email_verificator),
) -> dict:
    """Valida o código de verificação enviado pelo usuário."""
    await email_verificator.verify_code(current_user, data.code)
    
    return {
        "message": "E-mail verificado com sucesso."
    }
