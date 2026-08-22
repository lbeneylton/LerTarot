# Classe para hashes
from app.security.hasher import Argon2Hasher
from app.security.jwt_provider import JwtTokenService

# Erros
from app.core.exceptions import (
    ConflictError,
    UnauthorizedError, 
    VerificationError
)

# Tipos e modelos
from app.users.models import User

# UOW
from app.db.uow import SqlAlchemyUnitOfWork

# Schemas
from app.users.schemas import UserCreate, TokensResponse


# Verificador de email
from app.verify.services import CodeEmailService


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




class AuthenticationService:
    def __init__(
        self,
        uow: SqlAlchemyUnitOfWork,
        hasher: Argon2Hasher,
        provider_token: JwtTokenService,
    ) -> None:
        self.uow = uow
        self.hasher = hasher
        self.provider_token = provider_token

    def _generate_tokens(self, user: User) -> TokensResponse:
        """
        Gera access token e refresh token para o usuário.
        """
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
    
    def _revoke_all_tokens(self, user: User) -> User:
        # Revoga todos os tokens anteriores
        user.token_version += 1
        self.uow.users.save(user)
        return user

    def login(self, email_or_username: str, password: str) -> TokensResponse:
        """
        Autentica o usuário pelo e-mail ou username.

        Retorna:
            {
                "access_token": "...",
                "refresh_token": "..."
            }

        Lança UnauthorizedError caso:
        - usuário não exista;
        - usuário esteja inativo;
        - senha esteja incorreta.
        """
        if "@" in email_or_username:
            user = self.uow.users.get_active_by_email(
                email_or_username
            )
        else:
            user = self.uow.users.get_active_by_username(
                email_or_username
            )

        if user is None:
            raise UnauthorizedError("Credenciais inválidas")

        if not self.hasher.verify_hash(
            password,
            user.password_hash
        ):
            raise UnauthorizedError("Credenciais inválidas")

        # Se email não verificado
        if not user.email_verified:
            raise VerificationError("Email não verificado")

        user = self._revoke_all_tokens(user)
        
        return self._generate_tokens(user)
                
    def refresh(self, refresh_token: str | None) -> TokensResponse:
        """
        Gera um novo access token e
        com Refresh Token Rotation 
        gera um novo refresh token também.

        O refresh token não é armazenado no banco.
        Portanto, sua validade depende exclusivamente
        da assinatura e expiração do JWT.

        O JwtTokenService precisa disponibilizar um método
        para validar/decodificar refresh tokens.
        """
        if not refresh_token:
            raise UnauthorizedError(
                "Refresh token ausente"
            )
        
        payload = self.provider_token.decode_refresh_token(
            refresh_token
        )

        user_id = int(payload["sub"])
        
        with self.uow as uow:
            user = uow.users.get_active_by_id(user_id)
            if user is None:
                raise UnauthorizedError("Usuário não encontrado")

            # Compara a versão do token
            if payload["token_version"] != user.token_version:
                raise UnauthorizedError(
                    "Token revogado"
                )

            user.token_version += 1
            
            uow.users.save(user)
            uow.session.flush()

            return self._generate_tokens(user)

    def logout(self, refresh_token: str | None) -> str:
        """
        Logout.

        - Verifica se existe um refresh_token
        - Decode o token refresh
        - Verifica se existe o user  
        - Revoga Token
        - Apaga os Tokens dos cookies
        """
        if not refresh_token:
            raise UnauthorizedError(
                "Refresh token ausente"
            )
          
        payload = self.provider_token.decode_refresh_token(
            refresh_token
        )
        
        user_id = int(payload["sub"])
        user = self.uow.users.get_active_by_id(user_id)
        if not user:
            raise UnauthorizedError(
                "Usuário não encontrado"
            )

            
        self._revoke_all_tokens(user)
        # APAGAR COOKIES
        return "Usuário deslogado"

     
    
    
    
    
class OAuthService:
    def login_google(
        self,
        google_token: str,
    ) -> dict:
        """
        Login via Google.

        A validação do token do Google ainda precisa ser implementada.

        O ideal é criar um GoogleAuthService separado para:
        1. validar o token;
        2. obter email/nome/google_id;
        3. localizar ou criar o usuário;
        4. retornar os tokens da aplicação.
        """

        raise NotImplementedError(
            "Integração com Google ainda não implementada"
        )


class PasswordService:
    def __init__(self) -> None:
        pass

    # def recovery_password(self, email: str) -> None:
    #     """
    #     Solicita recuperação de senha.

    #     Gera um token temporário e envia para o e-mail.
    #     """

    #     user = self.uow.get_active_by_email(email)

    #     # Não revela se o e-mail existe
    #     if user is None:
    #         return None

    #     # Invalida tokens anteriores
    #     self.password_reset_repo.invalidate_user_tokens(user.id)

    #     # Token seguro
    #     token = secrets.token_urlsafe(32)

    #     # Validade de 15 minutos
    #     expires_at = (
    #         datetime.now(timezone.utc)
    #         + timedelta(minutes=15)
    #     )

    #     # Não salvar o token puro
    #     token_hash = self.hasher.hash_password(token)

    #     self.password_reset_repo.create(
    #         user_id=user.id,
    #         token_hash=token_hash,
    #         expires_at=expires_at,
    #         used=False,
    #     )

    #     self.password_reset_repo.session.flush()

    #     # Envia o token/link por e-mail
    #     self.email_sender.send_password_recovery(
    #         token,
    #         user.email,
    #     )

    #     return None

    # #
    # # Password
    # #
    # def reset_password(
    #     self,
    #     token: str,
    #     new_password: str,
    # ) -> None:
    #     """
    #     Redefine a senha usando um token de recuperação.
    #     """

    #     reset = self.password_reset_repo.get_active_tokens()

    #     now = datetime.now(timezone.utc)

    #     for item in reset:
    #         if item.used:
    #             continue

    #         if item.expires_at <= now:
    #             continue

    #         if self.hasher.verify_password(
    #             token,
    #             item.token_hash,
    #         ):
    #             user = self.uow.get_by_id(item.user_id)

    #             if user is None:
    #                 raise UnauthorizedError(
    #                     "Token inválido"
    #                 )

    #             user.password_hash = (
    #                 self.hasher.hash_password(new_password)
    #             )

    #             # Token só pode ser utilizado uma vez
    #             item.used = True

    #             self.uow.save(user)
    #             self.password_reset_repo.save(item)

    #             self.uow.session.flush()

    #             return None

    #     raise UnauthorizedError(
    #         "Token de recuperação inválido ou expirado"
    #     )

    # def change_password(
    #     self,
    #     user: User,
    #     current_password: str,
    #     new_password: str,
    # ) -> str:
    #     """
    #     Altera a senha de um usuário autenticado.
    #     """

    #     if not self.hasher.verify_password(
    #         current_password,
    #         user.password_hash,
    #     ):
    #         raise UnauthorizedError(
    #             "Senha atual inválida"
    #         )

    #     if current_password == new_password:
    #         raise ConflictError(
    #             "A nova senha deve ser diferente da senha atual"
    #         )

    #     user.password_hash = self.hasher.hash_password(
    #         new_password
    #     )

    #     self.uow.save(user)
    #     self.uow.session.flush()
    #     self.uow.session.refresh(user)
        
    #     return "Senha alterada"


 
 
 
 
#  PasswordResetToken
# ------------------
# id
# user_id
# token_hash
# expires_at
# used_at
# created_at