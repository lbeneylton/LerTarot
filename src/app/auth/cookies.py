# app/auth/cookies.py

from fastapi import Response, Cookie

from app.core.exceptions import UnauthorizedError

from app.security.jwt_provider import JwtTokenService
from app.users.services import UserService


ACCESS_MAX_AGE = 15 * 60
REFRESH_MAX_AGE = 7 * 24 * 60 * 60

ACCESS_PATH = "/"
REFRESH_PATH = "/auth/refresh"

# HTTPS
SECURE = False


def set_auth_cookies(
    response: Response,
    access_token: str,
    refresh_token: str,
) -> None:
    response.set_cookie(
        key="access_token",
        value=access_token,
        httponly=True,
        secure=SECURE,
        samesite="lax",
        max_age=ACCESS_MAX_AGE,
        path=ACCESS_PATH,
    )

    response.set_cookie(
        key="refresh_token",
        value=refresh_token,
        httponly=True,
        secure=SECURE,
        samesite="lax",
        max_age=REFRESH_MAX_AGE,
        path=REFRESH_PATH,
    )


def clear_auth_cookies(response: Response) -> None:
    response.delete_cookie(
        key="access_token",
        path=ACCESS_PATH,
    )

    response.delete_cookie(
        key="refresh_token",
        path=REFRESH_PATH,
    )


def get_current_user(
        token_provider: JwtTokenService,
        user_service: UserService,
        access_token: str | None = Cookie(default=None)
):

    if not access_token:
        raise UnauthorizedError("Não autenticado")

    payload = token_provider.decode_access_token(access_token)

    user_id = int(payload["sub"])

    return user_service.current_user(user_id)
