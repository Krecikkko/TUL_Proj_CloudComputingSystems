from pydantic import BaseModel, EmailStr, Field
from typing import Optional
from app.models.user import UserRole

class UserOut(BaseModel):
    id: int
    username: str
    email: EmailStr
    role: UserRole
    class Config:
        from_attributes = True

class UserUpdateIn(BaseModel):
    # Schema for updating a user's profile
    # Optional fields for partial updates
    username: Optional[str] = Field(None, min_length=3, max_length=50)
    email: Optional[EmailStr] = None
    # Password change requires the old password
    old_password: Optional[str] = None
    new_password: Optional[str] = Field(None, min_length=8, max_length=128)