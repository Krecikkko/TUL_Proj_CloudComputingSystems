from pydantic import BaseModel
from app.models.user import UserRole

class AdminRoleUpdateIn(BaseModel):
    role: UserRole