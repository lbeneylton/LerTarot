from pydantic import BaseModel, EmailStr
from typing import Any, Dict, Optional


class MessageRequest(BaseModel):
    to: EmailStr
    subject: str
    body: Optional[str] = None
    template: Optional[str] = None
    variables: Optional[Dict[str, Any]] = None