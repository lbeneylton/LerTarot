from pydantic import BaseModel, EmailStr, Field
from app.modules.users.models import UserRole


class UserCreate(BaseModel):
    username: str | None = Field(default=None, min_length=3, max_length=150)
    email: EmailStr
    password: str = Field(..., min_length=8)
    role: UserRole = UserRole.CLIENTE


class UserResponse(BaseModel):
    user_id: int
    username: str
    email: str
    role: str
    email_verified: bool

    class Config:
        from_attributes = True


class LoginRequest(BaseModel):
    email_or_username: str
    password: str = Field(..., min_length=8)


class TokensResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"


class AuthResponse(BaseModel):
    message: str


class RecoveryPasswordRequest(BaseModel):
    email: EmailStr


class VerifyTokenRequest(BaseModel):
    token: str


class ResetPasswordRequest(BaseModel):
    token: str
    new_password: str = Field(..., min_length=8)


class RecoveryResponse(BaseModel):
    message: str
