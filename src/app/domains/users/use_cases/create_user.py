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
            
            if uow.users.get_active_by_email(data.email):
                raise ConflictError("Este e-mail já está cadastrado.")
            
            if data.username:
                if uow.users.get_active_by_username(data.username):
                    raise ConflictError("Já existe um usuário com esse nome")

            password_hash = self.hasher.hash(data.password)

            if data.role == UserRole.CLIENTE:
                user = Client(
                    username=data.username,
                    email=data.email,
                    password_hash=password_hash,
                )
                
                key=(
                    f"welcome_cliente:"
                    f"{user.user_id}:"
                    f"{datetime.now(timezone.utc)}"
                )
                
                message = EmailMessage(
                    idempontency_key=key,
                    to=user.email,
                    subject="Seja bem vindo ao Ler Tarot",
                    body="welcome_cliente",
                    variables={
                        "user_name": user.username,
                        "year":"2026"
                    }
                )
                
                uow.emails.save(message)

            elif data.role == UserRole.READER:
                user = Reader(
                    username=data.username,
                    email=data.email,
                    password_hash=password_hash,
                )
                
                key=(
                    f"welcome_tarologo:"
                    f"{user.user_id}:"
                    f"{datetime.now(timezone.utc)}"
                )
                
                message = EmailMessage(
                    idempontency_key=key,
                    to=user.email,
                    subject="Seja bem vindo ao Ler Tarot",
                    body="welcome_tarologo",
                    variables={
                        "user_name": user.username,
                        "year":"2026"
                    }
                )
                
                uow.emails.save(message)

            else:
                user = User(
                    username=data.username,
                    email=data.email,
                    password_hash=password_hash,
                    role=UserRole.ADMIN,
                )

                

            user = uow.users.save(user)
            
    
        self.email_verificator.send_code(user)

        return user




class SendWelcomeEmail:
    
    def welcome_tarologo(self):
        pass
    
    
    def welcome_cliente(self):
        pass
        