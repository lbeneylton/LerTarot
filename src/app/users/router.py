from fastapi import APIRouter, status

from app.users.schemas import UserCreate, UserResponse
from app.users.services import UserService

router = APIRouter()


@router.post(
    "",
    response_model=UserResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Cadastrar usuário",
)
def create_user(data: UserCreate) -> UserResponse:
    user = UserService().create_user(data)
    return UserResponse.model_validate(user)
