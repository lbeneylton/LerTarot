from fastapi import Depends

from app.domains.users.services import (
    CreateUserService,
    AuthenticationService
)

from api.dependencies import  get_uow, get_email_verificator
from app.db.uow import SqlAlchemyUnitOfWork

from app.security.hasher import Argon2Hasher, get_hasher
from app.security.jwt_provider import JwtTokenService, get_token_provider
from app.domains.verify.services import CodeEmailService

def get_create_service(
    uow: SqlAlchemyUnitOfWork= Depends(get_uow),
    hasher: Argon2Hasher =Depends(get_hasher),
    email_verificator: CodeEmailService= Depends(get_email_verificator)
):
    return CreateUserService(
        uow,
        hasher,
        email_verificator
    )


def get_auth_service(
    uow: SqlAlchemyUnitOfWork = Depends(get_uow),
    hasher: Argon2Hasher = Depends(get_hasher),
    provider_token: JwtTokenService = Depends(
        get_token_provider
    ),
) -> AuthenticationService:

    return AuthenticationService(
        uow=uow,
        hasher=hasher,
        provider_token=provider_token,
    )