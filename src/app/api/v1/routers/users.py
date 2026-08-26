from fastapi import APIRouter, Depends
from app.api.dependencies import get_current_user
from app.modules.users.models import User
from app.modules.users.schemas import UserResponse

users_router = APIRouter(prefix="/users", tags=["users"])

@users_router.get("/me", response_model=UserResponse)
async def get_me(current_user: User = Depends(get_current_user)):
    """
    Retorna os dados do usuário atualmente autenticado (perfil).
    """
    return current_user
