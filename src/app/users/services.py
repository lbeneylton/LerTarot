# Classe para hashes
from app.security.hasher import Argon2Hasher
from app.security.jwt_provider import JwtTokenService

# Erros
from app.core.exceptions import ConflictError
from app.core.exceptions import UnauthorizedError

# Tipos e modelos
from app.users.models import User

# Repo e schemas
from app.users.repo import UserRepo
from app.users.schemas import UserCreate, TokensResponse

# Email Sender
from app.email.sender import EmailSender

class UserService:
    def __init__(
        self,
        repo: UserRepo,
        hasher: Argon2Hasher,
        token_provider: JwtTokenService,
        email_sender: EmailSender
    ) -> None:
        self.repo = repo
        self.hasher = hasher
        self.token_provider = token_provider
        self.email_sender = email_sender

    def _generate_tokens(self, user: User) -> TokensResponse:
        """
        Gera access token e refresh token para o usuário.
        """
        return TokensResponse(
            access_token=self.token_provider.create_access_token(
                user.user_id,
                user.token_version
            ),
            refresh_token=self.token_provider.create_refresh_token(
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

        password_hash = self.hasher.hash_password(data.password)

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

        if not self.hasher.verify_password(
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
        
        payload = self.token_provider.decode_refresh_token(
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
          
        payload = self.token_provider.decode_refresh_token(
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

    def request_email_code(self, user: User):
        """Gera código de autentificação e envia pro email"""
        
        # Gera codigo de autenticação com expiração
        code=""
        
        # Envia código pro email do usuario
        self.email_sender.send_code(code, user.email)
        pass

    def verify_email(self, user:User, code: str) -> bool:
        return True

    def recovery_password(
        self,
        email: str,
    ) -> None:
        """
        Solicita recuperação de senha.

        Fluxo recomendado:
        1. localizar usuário;
        2. gerar token de recuperação;
        3. salvar token com expiração;
        4. enviar e-mail.

        O token de recuperação NÃO deve ser o mesmo
        refresh token do usuário.
        """       

        user = self.repo.get_active_by_email(email)

        # Por segurança, normalmente não informamos
        # se o e-mail existe ou não.
        if user is None:
            return None

        raise NotImplementedError(
            "Fluxo de recuperação de senha ainda não implementado"
        )

    def change_password(
        self,
        user: User,
        current_password: str,
        new_password: str,
    ) -> str:
        """
        Altera a senha de um usuário autenticado.
        """

        if not self.hasher.verify_password(
            current_password,
            user.password_hash,
        ):
            raise UnauthorizedError(
                "Senha atual inválida"
            )

        if current_password == new_password:
            raise ConflictError(
                "A nova senha deve ser diferente da senha atual"
            )

        user.password_hash = self.hasher.hash_password(
            new_password
        )

        self.repo.save(user)
        self.repo.session.commit()
        self.repo.session.refresh(user)
        
        return "Senha alterada"

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
 