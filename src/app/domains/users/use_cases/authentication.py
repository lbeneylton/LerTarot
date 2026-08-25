from app.security.hasher import Argon2Hasher
from app.security.jwt_provider import JwtTokenService
from app.core.exceptions import UnauthorizedError
from app.domains.users.models import User
from app.db.uow import SqlAlchemyUnitOfWork
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

    async def _revoke_all_tokens(self, uow_instance, user: User) -> User:
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
        if not refresh_token:
            raise UnauthorizedError("Refresh token ausente")

        payload = self.provider_token.decode_refresh_token(refresh_token)
        user_id = int(payload["sub"])

        async with self.uow as uow:
            user = await uow.users.get_active_by_id(user_id)
            if not user:
                raise UnauthorizedError("Usuário não encontrado")

            await self._revoke_all_tokens(uow, user)
            return "Usuário deslogado"