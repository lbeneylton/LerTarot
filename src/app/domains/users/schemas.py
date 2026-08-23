from typing import Optional
from pydantic import BaseModel, ConfigDict, EmailStr, Field

from app.domains.users.enums import UserType


class UserCreate(BaseModel):
    username: Optional[str]
    email: EmailStr
    password: str = Field(..., min_length=8, max_length=128)
    role: UserType = UserType.CLIENTE

    model_config = ConfigDict(from_attributes=True)
    # foto_url: Optional[str] = Field(default=None, max_length=255)
    # bio: Optional[str] = Field(default=None, max_length=255)


class LoginRequest(BaseModel):
    email_or_username: str | EmailStr
    password: str = Field(..., min_length=8, max_length=128)

    model_config = ConfigDict(from_attributes=True)


class TokensResponse(BaseModel):
    access_token: str
    refresh_token: str


class AuthResponse(BaseModel):
    message: str
    model_config = ConfigDict(from_attributes=True)
    
    
    
class RecoveryPasswordRequest(BaseModel):
    email: EmailStr
    

class RecoveryResponse(AuthResponse):
    pass


class VerifyTokenRequest(BaseModel):
    token: str
    
class ResetPasswordRequest(BaseModel):
    token: str
    new_password: str