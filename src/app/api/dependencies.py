from fastapi import Depends, Header, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.core.exceptions import UnauthorizedError, ForbiddenError
from app.db.connection import get_session
from app.db.uow import SqlAlchemyUnitOfWork
from app.security.hasher import Argon2Hasher, get_hasher
from app.security.jwt_provider import JwtTokenService, get_token_provider

from app.modules.users.models import User, UserRole
from app.modules.auth.use_cases import CreateUserService, AuthenticationService
from app.modules.password_recovery.use_cases import PasswordRecoveryUseCase
from app.modules.email_verification.services import VerifyEmailService
from app.modules.emails.services import EmailService

security = HTTPBearer(auto_error=False)


# =====================================================================
# Database & UoW
# =====================================================================
def get_uow(
    session: AsyncSession = Depends(get_session),
) -> SqlAlchemyUnitOfWork:
    return SqlAlchemyUnitOfWork(session)


# =====================================================================
# Domain Services / Use Cases
# =====================================================================
def get_email_service(
    uow: SqlAlchemyUnitOfWork = Depends(get_uow),
) -> EmailService:
    return EmailService(uow)


def get_email_verificator(
    uow: SqlAlchemyUnitOfWork = Depends(get_uow),
    hasher: Argon2Hasher = Depends(get_hasher),
) -> VerifyEmailService:
    return VerifyEmailService(uow, hasher)


from app.core.contracts.notification import NotificationContract
from app.infrastructure.notifications.discord_notifier import DiscordNotifier

def get_notifier() -> NotificationContract:
    return DiscordNotifier()

def get_create_service(
    uow: SqlAlchemyUnitOfWork = Depends(get_uow),
    hasher: Argon2Hasher = Depends(get_hasher),
    email_verificator: VerifyEmailService = Depends(get_email_verificator),
    notifier: NotificationContract = Depends(get_notifier),
) -> CreateUserService:
    return CreateUserService(uow, hasher, email_verificator, notifier)


def get_auth_service(
    uow: SqlAlchemyUnitOfWork = Depends(get_uow),
    hasher: Argon2Hasher = Depends(get_hasher),
    provider_token: JwtTokenService = Depends(get_token_provider),
) -> AuthenticationService:
    return AuthenticationService(uow, hasher, provider_token)


def get_password_recovery_use_case(
    uow: SqlAlchemyUnitOfWork = Depends(get_uow),
    hasher: Argon2Hasher = Depends(get_hasher),
    email_service: EmailService = Depends(get_email_service),
) -> PasswordRecoveryUseCase:
    return PasswordRecoveryUseCase(uow, hasher, email_service)


# =====================================================================
# Authentication & Authorization Guards
# =====================================================================
async def get_current_user(
    credentials: HTTPAuthorizationCredentials | None = Depends(security),
    uow: SqlAlchemyUnitOfWork = Depends(get_uow),
    token_service: JwtTokenService = Depends(get_token_provider),
) -> User:
    """Extrai e valida o token JWT do header Authorization e retorna o usuário."""
    if not credentials:
        raise UnauthorizedError("Token de acesso ausente ou inválido")

    payload = token_service.decode_access_token(credentials.credentials)
    user_id_str = payload.get("sub")
    if not user_id_str:
        raise UnauthorizedError("Token de acesso ausente ou inválido")

    try:
        user_id = int(user_id_str)
    except ValueError:
        raise UnauthorizedError("Formato de ID de usuário inválido")

    async with uow:
        user = await uow.users.get_active_by_id(user_id)
        if not user:
            raise UnauthorizedError("Usuário não encontrado ou inativo")

        if str(payload.get("token_version")) != str(user.token_version):
            raise UnauthorizedError("Token revogado")

        return user


class RoleChecker:
    """Fábrica de dependências para validação de papeis de usuário."""
    def __init__(self, allowed_roles: list[UserRole]) -> None:
        self.allowed_roles = allowed_roles

    def __call__(self, current_user: User = Depends(get_current_user)) -> User:
        if current_user.role not in self.allowed_roles:
            raise ForbiddenError("Acesso negado para este tipo de usuário")
        return current_user


# =====================================================================
# Security Helpers
# =====================================================================
def verify_internal_token(x_internal_token: str = Header(...)) -> str:
    """Valida o header X-Internal-Token para rotas internas."""
    if x_internal_token != settings.internal_api_key:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Acesso não autorizado: token de comunicação interna inválido."
        )
    return x_internal_token
