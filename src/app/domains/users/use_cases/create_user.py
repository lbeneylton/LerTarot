from app.security.hasher import Argon2Hasher

# Tipos e modelos
from app.domains.users.models import User, Client, Reader , UserRole

# UOW
from app.db.uow import SqlAlchemyUnitOfWork

# Schemas
from app.domains.users.schemas import UserCreate


# Verificador de email
from app.domains.verify.services import VerifyEmailService

# Exceptions
from app.core.exceptions import ConflictError

# Criar mensagem na outbox
from app.domains.emails.models import EmailMessage

from datetime import datetime, timezone

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

    def create_user(self, data: UserCreate) -> User:
        """
        Cria um novo usuário.
        
        # validar email
        # validar username
        # hash senha
        # criar User
        # salvar User
        # enviar código
        # retornar User
        """
        with self.uow as uow:
            
            # 1. Validações
            if uow.users.get_active_by_email(data.email):
                raise ConflictError("Este e-mail já está cadastrado.")
            
            if data.username:
                if uow.users.get_active_by_username(data.username):
                    raise ConflictError("Já existe um usuário com esse nome")

            # 2. Hash
            password_hash = self.hasher.hash(data.password)

            # 3. Criar usuário
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

            # 4. Salvar usuário
            new_user = uow.users.save(user)
            
            # 5. Forçar INSERT e obter user_id
            uow.session.flush()

            # 6. Criar e-mail de boas-vindas
            if welcome_body:

                key = (
                    f"{welcome_prefix}:"
                    f"{new_user.user_id}:"
                    f"{datetime.now(timezone.utc)}"
                )

                message = EmailMessage(
                    idempotency_key=key,
                    to=new_user.email,
                    subject="Seja bem vindo ao Ler Tarot",
                    body=welcome_body,
                    variables={
                        "user_name": new_user.username,
                        "year": "2026",
                    },
                )

                uow.emails.save(message)

            # 7. Gerar código de verificação
            self.email_verificator.send_code(new_user)

        return new_user


class SendWelcomeEmail:
    
    def welcome_tarologo(self):
        pass
    
    
    def welcome_cliente(self):
        pass
        