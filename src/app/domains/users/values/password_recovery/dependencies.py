from fastapi import Depends

from app.db.uow import SqlAlchemyUnitOfWork
from app.security.hasher import Argon2Hasher, get_hasher
from app.domains.verify.services import CodeEmailService

from api.dependencies import  get_uow, get_email_verificator
from app.domains.users.use_cases.password_recovery import PasswordRecoveryUseCase

def get_password_recovery_use_case(
    uow: SqlAlchemyUnitOfWork = Depends(get_uow),
    hasher: Argon2Hasher = Depends(get_hasher),
    email_sender: CodeEmailService = Depends(get_email_verificator),
) -> PasswordRecoveryUseCase:

    return PasswordRecoveryUseCase(
        uow=uow,
        hasher=hasher,
        email_sender=email_sender,
    )