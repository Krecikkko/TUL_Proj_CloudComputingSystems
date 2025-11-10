from pydantic import BaseModel, EmailStr

class MeOut(BaseModel):
    id: int
    username: str
    email: EmailStr
    role: str
