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
from app.users.schemas import UserCreate


class UserService:
    def __init__(
        self,
        repo: UserRepo,
        hasher: Argon2Hasher,
        token_provider: JwtTokenService
    ) -> None:
        self.repo = repo
        self.hasher = hasher
        self.token_provider = token_provider

    def create_user(self, data: UserCreate) -> User:
        """
        Cria um novo usuário.
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

        return user

    def login(self, email_or_username: str, password: str):
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

        return {
            "access_token": self.token_provider.create_access_token(user.user_id),
            "refresh_token": self.token_provider.create_refresh_token(user.user_id)
        }

    def refresh(self, refresh_token: str) -> dict:
        """
        Gera um novo access token e um novo refresh token.

        O refresh token não é armazenado no banco.
        Portanto, sua validade depende exclusivamente
        da assinatura e expiração do JWT.

        O JwtTokenService precisa disponibilizar um método
        para validar/decodificar refresh tokens.
        """

        try:
            payload = self.token_provider.decode_refresh_token(
                refresh_token
            )
        except Exception:  # JOSEErro
            raise UnauthorizedError(
                "Refresh token inválido ou expirado"
            )

        user_id = int(payload["sub"])

        user = self.repo.get_active_by_id(user_id)

        if user is None:
            raise UnauthorizedError(
                "Usuário não encontrado"
            )

        return {
            "access_token": (
                self.token_provider.create_access_token(
                    user.user_id
                )
            ),
            "refresh_token": (
                self.token_provider.create_refresh_token(
                    user.user_id
                )
            ),
        }

    def logout(self, refresh_token: str | None = None) -> None:
        """
        Logout.

        Como os refresh tokens ainda não são armazenados/revogados,
        não existe invalidação real no servidor neste momento.

        No cliente, os tokens devem ser removidos.

        Quando implementar blacklist/revogação, este método deverá
        registrar o refresh token como revogado.
        """

        # Stateless JWT:
        # não há nada para persistir/revogar por enquanto.
        return None

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
    ) -> None:
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

    def current_user(
        self,
        user_id,
    ) -> User:
        """
        Retorna o usuário autenticado pelo ID contido no JWT.
        """

        user = self.repo.get_active_by_id(user_id)

        if user is None:
            raise UnauthorizedError(
                "Usuário não encontrado"
            )

        return user

    def _generate_tokens(self, user: User) -> dict:
        """
        Gera access token e refresh token para o usuário.
        """

        return {
            "access_token": (
                self.token_provider.create_access_token(
                    user.user_id
                )
            ),
            "refresh_token": (
                self.token_provider.create_refresh_token(
                    user.user_id
                )
            ),
        }
