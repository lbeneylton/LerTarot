from collections.abc import Callable

from sqlalchemy.orm import Session

from app.core.exceptions import ConflictError
from app.core.security.password import hash_password
from app.db import session as db_session
from app.db.unit_of_work import UnitOfWork
from app.users.enums import UserType
from app.users.models import Client, Reader, User
from app.users.repository import UserRepository
from app.users.schemas import UserCreate


def build_user(data: UserCreate) -> User:
    """Instancia Client, Reader ou User (admin) conforme o tipo."""
    common = {
        "name": data.name,
        "email": data.email,
        "password_hash": hash_password(data.password),
    }

    if data.user_type == UserType.client:
        return Client(**common)
    if data.user_type == UserType.reader:
        return Reader(**common, foto_url=data.foto_url, bio=data.bio)
    return User(**common, user_type=UserType.admin)


class UserService:
    def __init__(
        self,
        session_factory: Callable[[], Session] | None = None,
    ) -> None:
        self._session_factory = session_factory or db_session.SessionLocal

    def _verificar_email_disponivel(
        self,
        repository: UserRepository,
        email: str,
    ) -> None:
        if repository.get_active_by_email(email):
            raise ConflictError("Já existe um usuário com esse email")

    def create_user(self, data: UserCreate) -> User:
        with UnitOfWork(self._session_factory) as uow:
            assert uow.users is not None and uow.session is not None
            self._verificar_email_disponivel(uow.users, data.email)
            user = build_user(data)
            new_user = uow.users.create(user)
            uow.session.flush()
            uow.session.refresh(new_user)
            uow.session.expunge(new_user)
            return new_user
