# app/auth/cookies.py

from datetime import timedelta
from fastapi import Response, Cookie

from app.core.config import settings

from app.core.exceptions import UnauthorizedError

from app.security.jwt_provider import JwtTokenService
from app.users.services import UserService


# PATHS ROOTS 
ACCESS_PATH = "/"
REFRESH_PATH = "/auth/refresh"

class CookieManager:
    def __init__(self, access_age:int, refresh_age:int, secure:bool = True) -> None:
        self.access_age = access_age
        self.refresh_age = refresh_age
        self.secure = secure # HTTPS
    
    def set_auth_cookies(
        self,
        response: Response,
        access_token: str,
        refresh_token: str,
    ) -> None:
        response.set_cookie(
            key="access_token",
            value=access_token,
            httponly=True,
            secure=self.secure,
            samesite="lax",
            max_age=self.access_age,
            path=ACCESS_PATH,
        )

        response.set_cookie(
            key="refresh_token",
            value=refresh_token,
            httponly=True,
            secure=self.secure,
            samesite="lax",
            max_age=self.refresh_age,
            path=REFRESH_PATH,
        )


    def clear_auth_cookies(self, response: Response) -> None:
        response.delete_cookie(
            key="access_token",
            path=ACCESS_PATH,
        )

        response.delete_cookie(
            key="refresh_token",
            path=REFRESH_PATH,
        )


# def get_current_user(
#         token_provider: JwtTokenService,
#         user_service: UserService,
#         access_token: str | None = Cookie(default=None)
# ):

#     if not access_token:
#         raise UnauthorizedError("Não autenticado")

#     payload = token_provider.decode_access_token(access_token)

#     if not payload:
#         raise UnauthorizedError("Token inválido")

#     user_id = int(payload["sub"])

#     return user_service.current_user(user_id)



# MAX AGES
ACCESS_MAX_AGE = int(timedelta(minutes=settings.access_expire_minutes).total_seconds())
REFRESH_MAX_AGE = int(timedelta(days=settings.refresh_expire_days).total_seconds())


cookie_manager = CookieManager(
    ACCESS_MAX_AGE,
    REFRESH_MAX_AGE,
    False
)