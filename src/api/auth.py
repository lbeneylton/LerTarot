from fastapi import APIRouter, Response, Cookie, Depends, status

from app.auth.cookies import set_auth_cookies, clear_auth_cookies

from app.users.schemas import (
    UserCreate,
    LoginSchema,
    AuthResponse
)
from app.core.exceptions import UnauthorizedError
from app.users.services import UserService
from app.users.dependencies import get_user_service

auther = APIRouter(prefix="/auth", tags=["Auth"])


@auther.post(
    "/register",
    status_code=status.HTTP_201_CREATED,
    response_model=AuthResponse
)
def register(
    data: UserCreate,
    response: Response,
    service: UserService = Depends(get_user_service),
):
    user = service.create_user(data)

    tokens = service.generate_tokens(user)

    set_auth_cookies(
        response,
        tokens["access_token"],
        tokens["refresh_token"],
    )

    return {"message": "Registro realizado com sucesso"}


@auther.post(
    "/login",
    status_code=status.HTTP_202_ACCEPTED,
    response_model=AuthResponse
)
def login(
    data: LoginSchema,
    response: Response,
    service: UserService = Depends(get_user_service)
):
    tokens = service.login(
        data.email_or_username,
        data.password,
    )

    set_auth_cookies(
        response,
        tokens["access_token"],
        tokens["refresh_token"],
    )

    return {"message": "Login realizado com sucesso"}


@auther.post(
    "/logout",
    status_code=status.HTTP_202_ACCEPTED,
    response_model=AuthResponse
)
def logout(response: Response):
    clear_auth_cookies(response)
    return {"message": "Logout realizado"}


@auther.post(
    "/refresh",
    status_code=status.HTTP_202_ACCEPTED,
    response_model=AuthResponse
)
def refresh(
    response: Response,
    service: UserService = Depends(get_user_service),
    refresh_token: str | None = Cookie(default=None)
):
    if refresh_token is None:
        raise UnauthorizedError("Refresh token não encontrado")

    tokens = service.refresh(refresh_token)

    set_auth_cookies(
        response,
        tokens["access_token"],
        tokens["refresh_token"],
    )

    return {"message": "Token renovado"}
