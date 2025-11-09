from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.models.file import File

async def assert_user_can_download(db: AsyncSession, user_id: int, file_id: int) -> File:
    res = await db.execute(select(File).where(File.id == file_id))
    file = res.scalar_one_or_none()
    if not file:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="File not found")
    owner_id = getattr(file, "uploaded_by", None)
    is_shared = getattr(file, "is_shared", False)
    if owner_id != user_id and not is_shared:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="No permission for this file")
    return file

async def assert_user_can_delete(db: AsyncSession, user_id: int, file_id: int) -> File:
    res = await db.execute(select(File).where(File.id == file_id))
    file = res.scalar_one_or_none()
    if not file:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="File not found")
    owner_id = getattr(file, "uploaded_by", None)
    if owner_id != user_id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Only owner can delete file")
    return file
