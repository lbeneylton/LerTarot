from app.security.hasher import Argon2Hasher

# Tipos e modelos
from app.domains.users.models import User

# UOW
from app.db.uow import SqlAlchemyUnitOfWork

# Schemas
from app.domains.users.schemas import UserCreate


# Verificador de email
from app.domains.verify.services import CodeEmailService



class CreateUserService:
    def __init__(
        self,
        uow: SqlAlchemyUnitOfWork, 
        hasher: Argon2Hasher, 
        email_verificator: CodeEmailService
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

            password_hash = self.hasher.hash(data.password)

            user = User(
                email=data.email,
                username=data.username,
                password_hash=password_hash,
                role=data.role.value
            )

            uow.users.save(user)
            
    
        self.email_verificator.send_code(user)

        return user

