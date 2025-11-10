from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import Optional
import jwt  # if you prefer python-jose: from jose import jwt, JWTError

from app.db import get_session
from app.models.user import User
from app.utils.config import SECRET_KEY, ALGORITHM

# Simple HTTP Bearer (no OAuth2 password flow)
# Swagger UI will now show a single "Authorize" field to paste your JWT.
bearer_scheme = HTTPBearer()

async def get_current_user(
    creds: HTTPAuthorizationCredentials = Depends(bearer_scheme),
    db: AsyncSession = Depends(get_session),
) -> User:
    """Validate JWT from Authorization: Bearer <token>, decode it, and load the user."""
    token = creds.credentials
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
    except Exception as e:  # jeśli używasz jose: except JWTError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Invalid token: {e}",
        )

    sub = payload.get("sub")
    if not sub:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token: missing sub")

    # sub musi być stringiem; konwertujemy do int jako user_id
    try:
        user_id = int(sub)
    except (TypeError, ValueError):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token: sub must be a numeric string")

    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalars().first()
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="User not found")

    return user


def require_roles(*roles: str):
    """
    Decorator-style dependency for role-based access control.
    Usage:
        Depends(require_roles("admin"))
    It supports both Enum (user.role.name) and plain string roles.
    """
    async def _checker(user: User = Depends(get_current_user)) -> User:
        role_str = getattr(user.role, "name", str(user.role))
        if role_str not in roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Insufficient role",
            )
        return user
    return _checker
