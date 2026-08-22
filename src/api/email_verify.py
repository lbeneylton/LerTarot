from fastapi import APIRouter, Depends, BackgroundTasks, status

from app.domains.users.models import User
from app.auth.permissions import get_current_user
from app.domains.verify.schemas import VerifyEmailRequest
from app.domains.verify.services import CodeEmailService
from api.dependencies import get_email_verificator
from providers.emails.worker import email_worker

email_router = APIRouter(prefix="/email-verification", tags=["Email Verification"])


@email_router.post("/send", status_code=status.HTTP_200_OK)
def send_verification_email(
    background_tasks: BackgroundTasks,
    current_user: User = Depends(get_current_user),
    email_verificator: CodeEmailService = Depends(get_email_verificator),
) -> dict:
    """Gera e envia o código de verificação para o e-mail do usuário em segundo plano (outbox)."""
    email_verificator.send_code(current_user)
    
    # Executa o envio imediato em segundo plano sem bloquear a requisição HTTP
    background_tasks.add_task(email_worker.process_emails)
    
    return {
        "message": "Código de verificação enviado com sucesso."
    }


@email_router.post("/verify", status_code=status.HTTP_200_OK)
def verify_email(
    data: VerifyEmailRequest,
    current_user: User = Depends(get_current_user),
    email_verificator: CodeEmailService = Depends(get_email_verificator),
) -> dict:
    """Valida o código de verificação enviado pelo usuário."""
    email_verificator.verify_code(current_user, data.code)
    
    return {
        "message": "E-mail verificado com sucesso."
    }
