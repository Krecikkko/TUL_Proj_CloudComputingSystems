from pydantic import BaseModel, EmailStr
from datetime import datetime

class MeOut(BaseModel):
    id: int
    username: str
    email: EmailStr
    role: str
    created_at: datetime
