# Classe para hashes
from app.security.hasher import Argon2Hasher
from app.security.jwt_provider import JwtTokenService

# Erros
from app.core.exceptions import (
    UnauthorizedError, 
    VerificationError
)

# Tipos e modelos
from app.domains.users.models import User

# UOW
from app.db.uow import SqlAlchemyUnitOfWork

# Schemas
from app.domains.users.schemas import TokensResponse



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

     
    
    