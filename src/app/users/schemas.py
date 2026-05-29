from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict, EmailStr, Field

from app.users.enums import UserType


class UserCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=50)
    email: EmailStr
    password: str = Field(..., min_length=8, max_length=128)
    user_type: UserType = UserType.client
    foto_url: str | None = Field(default=None, max_length=255)
    bio: str | None = Field(default=None, max_length=255)


class UserResponse(BaseModel):
    user_id: UUID
    name: str
    email: EmailStr
    user_type: UserType
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)
