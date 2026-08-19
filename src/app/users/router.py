from fastapi import APIRouter, Depends, Response, Cookie, status

from app.auth.cookies import cookie_manager
from app.users.schemas import UserCreate, LoginSchema
from app.users.services import UserService
from app.user.dependecies import get_user_service

router = APIRouter(prefix="/auth")



@router.post("register")
def register(
    data : UserCreate,
    service: UserService = Depends(get_user_service),
):
    pass



@router.post("/login")
def login(
    data: LoginSchema,
    response: Response,
    service: UserService = Depends(get_user_service),
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
    
    
@router.post("/refresh")
def refresh(
    response: Response,
    refresh_token: str | None = Cookie(default=None),
    service: UserService = Depends(get_user_service),
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
    
@router.post("/logout")
def logout(
    response: Response,
    refresh_token: str | None = Cookie(default=None),
    service: UserService = Depends(get_user_service),
):
    service.logout(refresh_token)

    cookie_manager.clear_auth_cookies(response)

    return {
        "message": "Logout realizado com sucesso"
    }
