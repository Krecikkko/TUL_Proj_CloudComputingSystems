from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.models.file import File
from app.models.user import User # New import
from app.core.permissions_map import PERMISSIONS_MAP # New import (assuming you create this file)

def check_permission(user: User, action: str, resource: str) -> bool:
    
    # Checks if a user can perform an action on a resource based on their role.

    # This function does NOT check ownership; it checks role-based capability.
    # :param user: The User object.
    # :param action: The requested action (e.g., 'update', 'delete').
    # :param resource: The resource type (e.g., 'file', 'user_account').
    # :return: True if permission is granted, False otherwise.
    
    user_role_str = getattr(user.role, "name", str(user.role))
    
    if user_role_str not in PERMISSIONS_MAP:
        return False
        
    allowed_actions = PERMISSIONS_MAP[user_role_str].get(resource, [])
    return action in allowed_actions

async def assert_user_can_download(db: AsyncSession, user: User, file_id: int) -> File:
    # Checks if the user can download the file based on ownership or admin privileges."""
    res = await db.execute(select(File).where(File.id == file_id))
    file = res.scalar_one_or_none()
    
    if not file:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="File not found")
        
    owner_id = file.uploaded_by
    
    # 1. Admin check (global permission to read/download any file)
    if check_permission(user, "read", "file"):
        return file
        
    # 2. Owner check 
    if owner_id == user.id and check_permission(user, "read", "own_file"):
        return file

    raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="No permission for this file")

async def assert_user_can_delete(db: AsyncSession, user: User, file_id: int) -> File:
    # Checks if the user can delete the file based on ownership or admin privileges."""
    res = await db.execute(select(File).where(File.id == file_id))
    file = res.scalar_one_or_none()
    
    if not file:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="File not found")

    owner_id = file.uploaded_by

    # 1. Admin check 
    if check_permission(user, "delete", "file"):
        return file

    # 2. Owner check 
    if owner_id == user.id and check_permission(user, "delete", "own_file"):
        return file

    raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Only owner or admin can delete this file")