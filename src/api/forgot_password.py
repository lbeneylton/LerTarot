from fastapi import APIRouter, Depends

# Schemas
from app.domains.users.schemas import (
    RecoveryPasswordRequest,
    VerifyTokenRequest,
    ResetPasswordRequest,
    RecoveryResponse,
)

# UseCase e depdendecy
from app.domains.users.use_cases.password_recovery import PasswordRecoveryUseCase
from app.domains.users.values.password_recovery.dependencies import get_password_recovery_use_case

forgot_router = APIRouter(
    prefix="/forgot-password",
    tags=["Recovery Password"],
)


@forgot_router.post("")
def request_recovery(
    data: RecoveryPasswordRequest,
    service: PasswordRecoveryUseCase = Depends(get_password_recovery_use_case),
):
    service.recovery_password(data.email)

    return RecoveryResponse(
        message="Verifique seu email"
    )



@forgot_router.post("/reset-password")
def reset_password(
    data: ResetPasswordRequest,
    service: PasswordRecoveryUseCase = Depends(get_password_recovery_use_case),
):
    service.reset_password(
        token=data.token,
        new_password=data.new_password,
    )

    return RecoveryResponse(
        message="Senha alterada com sucesso"
    )