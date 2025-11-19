from fastapi import APIRouter, Depends, HTTPException, status, Path, Response
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import List

from ..db import get_session
from ..models.user import User
from ..schemas.user import UserOut
from ..schemas.admin import AdminRoleUpdateIn # Imported new schema
from ..utils.auth_deps import require_roles

router = APIRouter(prefix="/api/admin", tags=["Admin (User Management)"])

@router.get("/users", response_model=List[UserOut], summary="List all users (Admin only)")
async def list_all_users(
    db: AsyncSession = Depends(get_session),
    current_user: User = Depends(require_roles("admin")),
):
    # Retrieves a list of all user accounts.
    result = await db.execute(select(User).order_by(User.id))
    users = result.scalars().all()
    return [UserOut.model_validate(u) for u in users]

@router.delete("/users/{user_id}", status_code=status.HTTP_204_NO_CONTENT, summary="Delete a user (Admin only)")
async def delete_user_account(
    user_id: int = Path(..., description="ID of the user to delete"),
    db: AsyncSession = Depends(get_session),
    current_user: User = Depends(require_roles("admin")),
):
    # Deletes a user account and their associated data (files via cascade).
    if user_id == current_user.id:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Cannot delete your own admin account via this endpoint.")
        
    result = await db.execute(select(User).where(User.id == user_id))
    user_to_delete = result.scalars().first()
    
    if not user_to_delete:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")

    await db.delete(user_to_delete)
    await db.commit()
    
    # NOTE: Logging admin actions is skipped as the LogBook model's CheckConstraint
    # does not include 'delete_user' or 'change_role' actions.
    
    return Response(status_code=status.HTTP_204_NO_CONTENT)

@router.put("/users/{user_id}/role", response_model=UserOut, summary="Change a user's role (Admin only)")
async def update_user_role(
    payload: AdminRoleUpdateIn,
    user_id: int = Path(..., description="ID of the user to modify"),
    db: AsyncSession = Depends(get_session),
    current_user: User = Depends(require_roles("admin")),
):
    # Updates the role of a specified user (e.g., from 'user' to 'admin').
    result = await db.execute(select(User).where(User.id == user_id))
    user_to_update = result.scalars().first()
    
    if not user_to_update:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
        
    if user_id == current_user.id and payload.role != user_to_update.role:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Cannot change your own role via this endpoint.")
        
    user_to_update.role = payload.role
    db.add(user_to_update)
    await db.commit()
    await db.refresh(user_to_update)
    
    return UserOut.model_validate(user_to_update)