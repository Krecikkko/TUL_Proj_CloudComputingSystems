from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, BigInteger
from app.db import get_session
from app.models.user import User
from app.models.file import File
from app.schemas.user import UserOut, UserUpdateIn
from app.utils.auth_deps import get_current_user
from app.utils.security import hash_password, verify_password

router = APIRouter(prefix="/api/users", tags=["users"])

def format_bytes(bytes_value: int) -> str:
    # Converts a byte count into a human-readable string (KB, MB, GB).
    if bytes_value is None or bytes_value == 0:
        return "0 Bytes"
    if bytes_value < 1024:
        return f"{bytes_value} Bytes"
    if bytes_value < 1024 * 1024:
        return f"{bytes_value / 1024:.2f} KB"
    if bytes_value < 1024 * 1024 * 1024:
        return f"{bytes_value / (1024 * 1024):.2f} MB"
    return f"{bytes_value / (1024 * 1024 * 1024):.2f} GB"

@router.put("/updateme", response_model=UserOut, summary="Update current user's profile")
async def update_user_profile(
    payload: UserUpdateIn,
    db: AsyncSession = Depends(get_session),
    current_user: User = Depends(get_current_user),
):
    # Allows authenticated users to update their username, email, and password."""
    
    updated = False
    
    # 1. Update Username/Email
    if payload.username is not None and payload.username != current_user.username:
        # Check for uniqueness
        res = await db.execute(select(User).where(User.username == payload.username))
        if res.scalars().first():
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Username already taken")
        current_user.username = payload.username
        updated = True

    if payload.email is not None and payload.email != current_user.email:
        # Check for uniqueness
        res = await db.execute(select(User).where(User.email == payload.email))
        if res.scalars().first():
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Email already registered")
        current_user.email = payload.email
        updated = True

    # 2. Update Password
    if payload.new_password is not None:
        if not payload.old_password:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Old password is required to set a new password")
        
        # Verify old password
        if not verify_password(payload.old_password, current_user.hashed_password):
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid old password")
        
        # Hash and set new password
        current_user.hashed_password = hash_password(payload.new_password)
        updated = True

    if updated:
        db.add(current_user)
        await db.commit()
        await db.refresh(current_user)

    return UserOut.model_validate(current_user)

@router.get("/stats", summary="Get statistics for the current user")
async def get_user_stats(
    db: AsyncSession = Depends(get_session),
    current_user: User = Depends(get_current_user),
):
    # Provides file count and total storage used by the authenticated user.
    # 1. Count files uploaded
    files_uploaded_res = await db.execute(
        select(func.count(File.id))
        .where(File.uploaded_by == current_user.id)
    )
    files_uploaded = files_uploaded_res.scalar_one()

    # 2. Calculate total storage used (sum of File.size)
    # Cast to BigInteger for safe summation on large datasets
    storage_used_res = await db.execute(
        select(func.sum(File.size).cast(BigInteger))
        .where(File.uploaded_by == current_user.id)
    )
    # sum() returns None if no rows match
    total_bytes = storage_used_res.scalar_one() or 0
    
    return {
        "files_uploaded": files_uploaded,
        "storage_used": format_bytes(total_bytes)
    }