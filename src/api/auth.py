# FastAPI
from fastapi import APIRouter, Response, Cookie, Depends, status

# Schemas
from app.users.schemas import (
    UserCreate,
    LoginRequest,
    AuthResponse
)

# Cookies manager
from app.security.cookies import cookie_manager

# Service e dependencies
from app.users.services import AuthenticationService, CreateUserService
from app.users.dependencies import get_auth_service, get_create_service


# Roteador
auth_router = APIRouter(prefix="/auth", tags=["Auth"])



@auth_router.post(
    "/register",
    status_code=status.HTTP_201_CREATED,
    response_model=AuthResponse,
    summary="Registro e login de um usuário"
)
def register(
    data : UserCreate,
    response: Response,
    create_service: CreateUserService = Depends(get_create_service),
    login_service: AuthenticationService = Depends(get_auth_service)
):
    user = create_service.create_user(data)
    
    tokens = login_service.login(
        email_or_username=str(user.email) or str(user.username),
        password=data.password,
    )
    
    cookie_manager.set_auth_cookies(
        response=response,
        access_token=tokens.access_token,
        refresh_token=tokens.refresh_token,
    )
    
    return {"message": "Registro realizado com sucesso"}


@auth_router.post(
    "/login",
    status_code=status.HTTP_202_ACCEPTED,
    response_model=AuthResponse,
    summary="Login de um usuário"
)
def login(
    data: LoginRequest,
    response: Response,
    service: AuthenticationService = Depends(get_auth_service),
):
    tokens = service.login(
        data.email_or_username,
        data.password,
    )

    cookie_manager.set_auth_cookies(
        response=response,
        access_token=tokens.access_token,
        refresh_token=tokens.refresh_token,
    )

    return {
        "message": "Login realizado com sucesso"
    }
    
    
@auth_router.post(
    "/refresh",
    status_code=status.HTTP_202_ACCEPTED,
    response_model=AuthResponse,
    summary="Refresh e revogação dos tokens"
)
def refresh(
    response: Response,
    refresh_token: str | None = Cookie(default=None),
    service: AuthenticationService = Depends(get_auth_service),
):
    tokens = service.refresh(refresh_token)

    cookie_manager.set_auth_cookies(
        response=response,
        access_token=tokens.access_token,
        refresh_token=tokens.refresh_token,
    )

    return {
        "message": "Token renovado"
    }
    
    
@auth_router.post(
    "/logout",
    status_code=status.HTTP_202_ACCEPTED,
    response_model=AuthResponse,
    summary="Revogação dos tokens"
)
def logout(
    response: Response,
    refresh_token: str | None = Cookie(default=None),
    service: AuthenticationService = Depends(get_auth_service),
):
    service.logout(refresh_token)
    cookie_manager.clear_auth_cookies(response)

    return {
        "message": "Logout realizado com sucesso"
    }
