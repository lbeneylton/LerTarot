from pydantic import BaseModel, EmailStr
from typing import Any, Dict, Optional
from datetime import datetime


class MessageRequest(BaseModel):
    to: EmailStr
    subject: str
    body: Optional[str] = None
    template: Optional[str] = None
    variables: Optional[Dict[str, Any]] = None


class MessageResponse(BaseModel):
    message_id: int
    to: str
    subject: str
    template: Optional[str] = None
    body: str
    status: str
    attempts: int
    next_retry_at: Optional[datetime] = None
    created_at: datetime
    sent_at: Optional[datetime] = None
    error: Optional[str] = None