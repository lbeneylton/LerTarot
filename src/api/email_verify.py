# FastAPI
from fastapi import APIRouter, Depends, status

# Session
from sqlalchemy.orm import Session
from app.db.connection import get_session

# User 
from app.users.models import User
from app.auth.permissions import get_current_user

# Email
from app.verify.schemas import VerifyEmailRequest
from app.verify.services import VerificatorEmailService
from app.verify.sender import EmailSender

email_router = APIRouter(prefix="/email-verification", tags=["Email Verification"])

@email_router.post("/send")
def send_verification_email(
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session),
    
):
    
    # Deve ativar o emailsender

    # service = EmailVerificationService(
        
    # )

    # service.send_code(current_user)

    return {
        "message": "Código enviado"
    }


@email_router.post("/verify")
def verify_email(
    data: VerifyEmailRequest,
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session),
):
    # service = EmailVerificationService(
    #     session=session,
    #     email_sender=email_sender,
    # )

    # service.verify_code(
    #     user=current_user,
    #     code=data.code,
    # )

    return {
        "message": "Email verificado com sucesso"
    }
