from datetime import datetime, timezone
from dataclasses import dataclass

from app.security.hasher import Argon2Hasher
from app.domains.users.models import User, Client, Reader, UserRole
from app.db.uow import SqlAlchemyUnitOfWork
from app.domains.users.schemas import UserCreate
from app.domains.verify.services import VerifyEmailService
from app.core.exceptions import ConflictError
from app.domains.emails.models import EmailMessage


@dataclass
class CreatedUser:
    user_id: int
    email: str
    username: str | None


class CreateUserService:
    def __init__(
        self,
        uow: SqlAlchemyUnitOfWork, 
        hasher: Argon2Hasher, 
        email_verificator: VerifyEmailService
    ) -> None:
        self.uow = uow
        self.hasher = hasher
        self.email_verificator = email_verificator

    async def create_user(self, data: UserCreate) -> CreatedUser:
        """Cria um novo usuário e dispara e-mails de boas-vindas e verificação."""
        async with self.uow as uow:
            if await uow.users.get_active_by_email(data.email):
                raise ConflictError("Este e-mail já está cadastrado.")
            
            if data.username:
                if await uow.users.get_active_by_username(data.username):
                    raise ConflictError("Já existe um usuário com esse nome")

            password_hash = self.hasher.hash(data.password)

            if data.role == UserRole.CLIENTE:
                user = Client(
                    username=data.username,
                    email=data.email,
                    password_hash=password_hash,
                )
                welcome_body = "welcome_cliente"
                welcome_prefix = "welcome_cliente"
            elif data.role == UserRole.READER:
                user = Reader(
                    username=data.username,
                    email=data.email,
                    password_hash=password_hash,
                )
                welcome_body = "welcome_tarologo"
                welcome_prefix = "welcome_tarologo"
            else:
                user = User(
                    username=data.username,
                    email=data.email,
                    password_hash=password_hash,
                    role=UserRole.ADMIN,
                )
                welcome_body = None
                welcome_prefix = None

            new_user = await uow.users.save(user)
            await uow.session.flush()
            
            result = CreatedUser(
                user_id=new_user.user_id,
                email=new_user.email,
                username=new_user.username,
            )

            if welcome_body:
                key = f"{welcome_prefix}:{new_user.user_id}:{datetime.now(timezone.utc).timestamp()}"
                message = EmailMessage(
                    idempotency_key=key,
                    to=new_user.email,
                    subject="Seja bem vindo ao Ler Tarot",
                    template=welcome_body,
                    body=welcome_body,
                    variables={
                        "user_name": new_user.username or "Usuário",
                        "year": datetime.now(timezone.utc).year,
                        "dashboard_url": "lertarot.com/dashboard",
                    },
                )
                await uow.emails.save(message)

            await self.email_verificator.send_code(new_user)
            return result