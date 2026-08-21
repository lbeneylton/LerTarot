from fastapi import Depends

from app.db.connection import get_session
from app.db.contract import SessionContract
from app.db.uow import SqlAlchemyUnitOfWork


from app.security.hasher import Argon2Hasher, get_hasher
from app.verify.services import VerificatorEmailService
from emails.interface import EmailSender, get_sender


def get_uow(
    session: SessionContract = Depends(get_session),
) -> SqlAlchemyUnitOfWork:
    return SqlAlchemyUnitOfWork(session)



def get_email_verificator(
    uow: SqlAlchemyUnitOfWork= Depends(get_uow),
    hasher: Argon2Hasher= Depends(get_hasher),
    email_sender = Depends()
    )-> VerificatorEmailService:
    return VerificatorEmailService(
        uow,
        hasher,
        email_sender
    )