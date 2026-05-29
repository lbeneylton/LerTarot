from fastapi import APIRouter, status

from app.auth.schemas import LoginRequest, TokenResponse
from app.auth.services import AuthService

router = APIRouter()


@router.post(
    "/login",
    response_model=TokenResponse,
    status_code=status.HTTP_200_OK,
    summary="Realizar login do usuário",
)
def login(data: LoginRequest) -> TokenResponse:
    """
    Realiza o login de um usuário autenticando seu e-mail e senha.

    Retorna um token de acesso JWT.
    """
    token = AuthService().login(data.email, data.password)
    return TokenResponse(access_token=token)
