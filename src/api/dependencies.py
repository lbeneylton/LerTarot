from fastapi import Depends

from app.db.connection import get_session
from app.db.contract import SessionContract
from app.db.uow import SqlAlchemyUnitOfWork


from app.security.hasher import Argon2Hasher, get_hasher
from app.domains.verify.services import VerifyEmailService
from providers.email_sender.get_sender import get_sender


def get_uow(
    session: SessionContract = Depends(get_session),
) -> SqlAlchemyUnitOfWork:
    return SqlAlchemyUnitOfWork(session)



def get_email_verificator(
    uow: SqlAlchemyUnitOfWork = Depends(get_uow),
    hasher: Argon2Hasher = Depends(get_hasher)
) -> VerifyEmailService:
    return VerifyEmailService(
        uow,
        hasher
    )


from fastapi import Header, HTTPException, status
from app.core.config import settings

def verify_internal_token(x_internal_token: str = Header(...)) -> str:
    """Valida se o token informado no header X-Internal-Token é válido."""
    if x_internal_token != settings.internal_api_key:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Acesso não autorizado: token de comunicação interna inválido."
        )
    return x_internal_token


# from app.domains.emails.services import EmailService

# def get_email_service(uow: SqlAlchemyUnitOfWork = Depends(get_uow)) -> EmailService:
#     return EmailService(uow)