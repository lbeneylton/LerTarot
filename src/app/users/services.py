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

# Repo e schemas
from app.users.repo import UserRepo
from app.users.schemas import UserCreate, TokensResponse

# Email Sender e secrets
from app.emails.sender import EmailSender

class UserService:
    def __init__(
        self,
        repo: UserRepo,
        hasher: Argon2Hasher,
        provider_token: JwtTokenService,
        email_sender: EmailSender
    ) -> None:
        self.repo = repo
        self.hasher = hasher
        self.provider_token = provider_token
        self.email_sender = email_sender

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
    
    def _revoke_token(self, user: User) -> User:
        # Revoga todos os tokens anteriores
        user.token_version += 1

        self.repo.save(user)
        self.repo.session.commit()
        self.repo.session.refresh(user)
        
        return user

    def email_is_verified(self, user: User) :
        if user.email_verified:
            raise  VerificationError(
                "Email já verificado"
            )

    def create_user(self, data: UserCreate) -> User:
        """
        Cria um novo usuário.
        
        TODO diminuir acesso ao banco utilziando analise de constraints UNIQUE
        """
        if self.repo.get_active_by_email(data.email):
            raise ConflictError("Já existe um usuário com esse email")

        if data.username:
            if self.repo.get_active_by_username(data.username):
                raise ConflictError("Username já cadastrado")

        password_hash = self.hasher.hash(data.password)

        user = User(
            email=data.email,
            username=data.username,
            password_hash=password_hash,
            role=data.role.value
        )

        self.repo.save(user)
        self.repo.session.commit()
        self.repo.session.refresh(user)

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
            user = self.repo.get_active_by_email(
                email_or_username
            )
        else:
            user = self.repo.get_active_by_username(
                email_or_username
            )

        if user is None:
            raise UnauthorizedError("Credenciais inválidas")

        if not self.hasher.verify_hash(
            password,
            user.password_hash
        ):
            raise UnauthorizedError("Credenciais inválidas")

        user = self._revoke_token(user)
        
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

        user = self.repo.get_active_by_id(user_id)
        if not user:
            raise UnauthorizedError("Usuário não encontrado")


        token_version = payload["token_version"]

        if token_version != user.token_version:
            raise UnauthorizedError(
                "Token revogado"
            )

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
        user = self.repo.get_active_by_id(user_id)
        if not user:
            raise UnauthorizedError(
                "Usuário não encontrado"
            )

            
        self._revoke_token(user)
        # APAGAR COOKIES
        return "Usuário deslogado"




    # def recovery_password(self, email: str) -> None:
    #     """
    #     Solicita recuperação de senha.

    #     Gera um token temporário e envia para o e-mail.
    #     """

    #     user = self.repo.get_active_by_email(email)

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

    #     self.password_reset_repo.session.commit()

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
    #             user = self.repo.get_by_id(item.user_id)

    #             if user is None:
    #                 raise UnauthorizedError(
    #                     "Token inválido"
    #                 )

    #             user.password_hash = (
    #                 self.hasher.hash_password(new_password)
    #             )

    #             # Token só pode ser utilizado uma vez
    #             item.used = True

    #             self.repo.save(user)
    #             self.password_reset_repo.save(item)

    #             self.repo.session.commit()

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

    #     self.repo.save(user)
    #     self.repo.session.commit()
    #     self.repo.session.refresh(user)
        
    #     return "Senha alterada"

    #
    # Login Provider
    #
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
 
 
 
 
#  PasswordResetToken
# ------------------
# id
# user_id
# token_hash
# expires_at
# used
# created_at