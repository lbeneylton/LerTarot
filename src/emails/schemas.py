from pydantic import BaseModel, EmailStr, Field

class MessageRequest(BaseModel):
    to: EmailStr
    subject: str
    template: str
    variables: dict