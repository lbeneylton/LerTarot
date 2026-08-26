from datetime import datetime, timezone
from dataclasses import dataclass

from app.core.contracts.uow import UnitOfWorkContract
from app.core.contracts.security import PasswordHasherContract, TokenServiceContract
from app.core.exceptions import UnauthorizedError, ConflictError
from app.modules.users.models import User, Client, Reader, UserRole
from app.modules.users.schemas import UserCreate, TokensResponse
from app.modules.email_verification.services import VerifyEmailService
from app.modules.emails.models import EmailMessage


@dataclass
class CreatedUser:
    user_id: int
    email: str
    username: str | None


from app.core.contracts.notification import NotificationContract

class CreateUserService:
    def __init__(
        self,
        uow: UnitOfWorkContract, 
        hasher: PasswordHasherContract, 
        email_verificator: VerifyEmailService,
        notifier: NotificationContract,
    ) -> None:
        self.uow = uow
        self.hasher = hasher
        self.email_verificator = email_verificator
        self.notifier = notifier

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
                welcome_body = "Olá, seja bem vindo ao Ler Tarot! Esperamos que você encontre as respostas que procura."
                welcome_prefix = "welcome_cliente"
            elif data.role == UserRole.READER:
                user = Reader(
                    username=data.username,
                    email=data.email,
                    password_hash=password_hash,
                )
                welcome_body = "Olá, seja bem vindo ao Ler Tarot! Acesse o dashboard para configurar seu perfil e começar a atender."
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
                    subject=welcome_body,
                    template=welcome_prefix,
                    variables={
                        "user_name": new_user.username,
                        "year": datetime.now(timezone.utc).year,
                        "dashboard_url": "lertarot.com/dashboard",
                    },
                )
                await uow.emails.save(message)

            # Notifica auditoria de negócio (em background, sem prender a transação)
            await self.notifier.notify_new_user(user_name=new_user.username or "Sem nome", user_email=new_user.email)
            
            return result


class AuthenticationService:
    def __init__(
        self,
        uow: UnitOfWorkContract,
        hasher: PasswordHasherContract,
        provider_token: TokenServiceContract,
    ) -> None:
        self.uow = uow
        self.hasher = hasher
        self.provider_token = provider_token

    def _generate_tokens(self, user: User) -> TokensResponse:
        return TokensResponse(
            access_token=self.provider_token.create_access_token(
                user.user_id,
                user.token_version
            ),
            refresh_token=self.provider_token.create_refresh_token(
                user.user_id,
                user.token_version
            )
        )

    async def _revoke_all_tokens(self, uow_instance: UnitOfWorkContract, user: User) -> User:
        user.token_version += 1
        await uow_instance.users.save(user)
        return user

    async def login(self, email_or_username: str, password: str) -> TokensResponse:
        async with self.uow as uow:
            if "@" in email_or_username:
                user = await uow.users.get_active_by_email(email_or_username)
            else:
                user = await uow.users.get_active_by_username(email_or_username)

            if user is None:
                raise UnauthorizedError("Credenciais inválidas")

            if not self.hasher.verify_hash(password, user.password_hash):
                raise UnauthorizedError("Credenciais inválidas")

            user = await self._revoke_all_tokens(uow, user)
            return self._generate_tokens(user)

    async def refresh(self, refresh_token: str | None) -> TokensResponse:
        if not refresh_token:
            raise UnauthorizedError("Refresh token ausente")

        payload = self.provider_token.decode_refresh_token(refresh_token)
        user_id = int(payload["sub"])

        async with self.uow as uow:
            user = await uow.users.get_active_by_id(user_id)
            if user is None:
                raise UnauthorizedError("Usuário não encontrado")

            if str(payload.get("token_version")) != str(user.token_version):
                raise UnauthorizedError("Token revogado")

            user.token_version += 1
            await uow.users.save(user)
            await uow.session.flush()

            return self._generate_tokens(user)

    async def logout(self, refresh_token: str | None) -> str:
        if refresh_token:
            try:
                payload = self.provider_token.decode_refresh_token(refresh_token)
                user_id_str = payload.get("sub")
                if user_id_str:
                    user_id = int(user_id_str)
                    async with self.uow as uow:
                        user = await uow.users.get_active_by_id(user_id)
                        if user:
                            await self._revoke_all_tokens(uow, user)
            except Exception:
                pass
        return "Usuário deslogado com sucesso"
