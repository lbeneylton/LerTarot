from pydantic import BaseModel, EmailStr, Field


class RecoveryPasswordRequest(BaseModel):
    email: EmailStr


class VerifyTokenRequest(BaseModel):
    token: str


class ResetPasswordRequest(BaseModel):
    token: str
    new_password: str = Field(..., min_length=8)


class RecoveryResponse(BaseModel):
    message: str
