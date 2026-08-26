from fastapi import APIRouter, Depends

from app.modules.password_recovery.schemas import (
    RecoveryPasswordRequest,
    ResetPasswordRequest,
    RecoveryResponse,
)
from app.modules.password_recovery.use_cases import PasswordRecoveryUseCase
from app.api.dependencies import get_password_recovery_use_case

forgot_router = APIRouter(
    prefix="/forgot-password",
    tags=["Recovery Password"],
)


@forgot_router.post("", response_model=RecoveryResponse)
async def request_recovery(
    data: RecoveryPasswordRequest,
    service: PasswordRecoveryUseCase = Depends(get_password_recovery_use_case),
):
    await service.recovery_password(data.email)
    return RecoveryResponse(message="Verifique seu email")


@forgot_router.post("/reset-password", response_model=RecoveryResponse)
async def reset_password(
    data: ResetPasswordRequest,
    service: PasswordRecoveryUseCase = Depends(get_password_recovery_use_case),
):
    await service.reset_password(
        token=data.token,
        new_password=data.new_password,
    )
    return RecoveryResponse(message="Senha alterada com sucesso")


@forgot_router.get("/verify-token/{token}", response_model=RecoveryResponse)
async def verify_token(
    token: str,
    service: PasswordRecoveryUseCase = Depends(get_password_recovery_use_case),
):
    await service.verify_token(token)
    return RecoveryResponse(message="Token válido")
