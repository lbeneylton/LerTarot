from src.app.users.repository import UserRepository
from src.app.users.models import User

from src.app.core.security.password import hash_password
from src.app.core.exceptions import ConflictError


class UserService:
    def __init__(self, repository) -> None:
        self.repository: UserRepository = repository

    def _verificar_email_disponivel(self, email: str) -> None:
        if self.repository.get_active_by_email(email):
            raise ConflictError("Já existe um usuário com esse email")

    def create_user(self, data) -> User:
        self._verificar_email_disponivel(data.email)

        user = User(
            nome=data.nome,
            email=data.email,
            password_hash=hash_password(data.password),
            role=data.role
        )

        new_user = self.repository.create(user)

        # 4. commit (por enquanto aqui, depois usar uma unit of work)
        self.repository.session.commit()
        self.repository.session.refresh(new_user)

        return new_user
