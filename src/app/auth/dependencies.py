from uuid import UUID
from fastapi import Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

from app.core.exceptions import UnauthorizedError, ForbiddenError
from app.core.security.jwt import decode_token
from app.users.enums import UserType
from app.users.models import User
from app.users.services import UserService

security = HTTPBearer(auto_error=False)


def get_current_user(
    credentials: HTTPAuthorizationCredentials | None = Depends(security),
    user_service: UserService = Depends(UserService),
) -> User:
    """
    Dependência para obter o usuário atualmente autenticado a partir do token JWT.

    Valida o token JWT e retorna o modelo do usuário correspondente se estiver ativo.
    Caso contrário, lança UnauthorizedError.
    """
    if not credentials:
        raise UnauthorizedError("Token de acesso ausente ou inválido")

    token = credentials.credentials
    payload = decode_token(token)
    if not payload:
        raise UnauthorizedError("Token de acesso ausente ou inválido")

    user_id_str = payload.get("sub")
    if not user_id_str:
        raise UnauthorizedError("Token de acesso ausente ou inválido")

    try:
        user_id = UUID(user_id_str)
    except ValueError:
        raise UnauthorizedError("Token de acesso ausente ou inválido")

    user = user_service.get_user_by_id(user_id)
    if not user:
        raise UnauthorizedError("Usuário não encontrado ou inativo")

    return user


class RoleChecker:
    """
    Classe fábrica de dependências para restringir o acesso por tipos de usuário (UserType).
    """

    def __init__(self, allowed_roles: list[UserType]) -> None:
        self.allowed_roles = allowed_roles

    def __call__(self, current_user: User = Depends(get_current_user)) -> User:
        """
        Garante que o usuário autenticado tenha um dos tipos permitidos.

        Caso contrário, lança ForbiddenError.
        """
        if current_user.user_type not in self.allowed_roles:
            raise ForbiddenError("Acesso negado para este tipo de usuário")
        return current_user
