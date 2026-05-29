from pydantic import BaseModel, EmailStr, Field


class LoginRequest(BaseModel):
    """Esquema para requisição de login."""
    email: EmailStr
    password: str = Field(..., min_length=8, max_length=128)


class TokenResponse(BaseModel):
    """Esquema de resposta contendo o token JWT."""
    access_token: str
    token_type: str = "bearer"
