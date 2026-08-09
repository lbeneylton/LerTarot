from datetime import datetime
from uuid import UUID
from typing import Optional

from pydantic import BaseModel, ConfigDict, EmailStr, Field

from app.users.enums import UserType


class UserCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=50)
    username: str | None
    email: EmailStr
    password: str = Field(..., min_length=8, max_length=128)
    role: UserType = UserType.CLIENTE

    # foto_url: Optional[str] = Field(default=None, max_length=255)
    # bio: Optional[str] = Field(default=None, max_length=255)


class UserResponse(BaseModel):
    user_id: UUID
    name: str
    email: EmailStr
    role: UserType
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)
