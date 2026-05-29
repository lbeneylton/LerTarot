from collections.abc import Callable
from sqlalchemy.orm import Session

from app.core.exceptions import UnauthorizedError
from app.core.security.password import verify_password
from app.core.security.jwt import create_access_token
from app.db import session as db_session
from app.db.unit_of_work import UnitOfWork


class AuthService:
    """Serviço responsável pelo fluxo de autenticação."""

    def __init__(
        self,
        session_factory: Callable[[], Session] | None = None,
    ) -> None:
        self._session_factory = session_factory or db_session.SessionLocal

    def login(self, email: str, password: str) -> str:
        """
        Autentica o usuário pelo e-mail e senha.

        Lança UnauthorizedError caso o e-mail não seja encontrado ou a senha seja incorreta.
        Retorna o token de acesso JWT.
        """
        with UnitOfWork(self._session_factory) as uow:
            assert uow.users is not None
            user = uow.users.get_active_by_email(email)

            if not user:
                raise UnauthorizedError("E-mail ou senha incorretos")

            if not verify_password(password, user.password_hash):
                raise UnauthorizedError("E-mail ou senha incorretos")

            payload = {
                "sub": str(user.user_id),
                "user_type": user.user_type.value,
            }
            return create_access_token(payload)
