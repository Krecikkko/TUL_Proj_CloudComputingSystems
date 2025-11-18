# backend/app/routes/share.py (NOWY PLIK)

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import FileResponse
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from pathlib import Path
from ..db import get_session
from ..models.file import File
from ..utils.logging import log_action
from ..storage import _abs_under_root 

router = APIRouter(prefix="", tags=["Share (Public)"]) # Router na głównym ścieżce /

@router.get("/share/{share_id}")
async def public_download_file(
    share_id: str,
    db: AsyncSession = Depends(get_session)
):
    # 1. Znajdź plik po ID udostępniania
    result = await db.execute(
        select(File).where(File.share_link_id == share_id)
    )
    file_obj = result.scalars().first()
    
    if not file_obj:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Share link is invalid or file was deleted")
    
    # 2. Pobierz ścieżkę (plik musi istnieć fizycznie)
    storage_path = file_obj.filepath
    abs_path = _abs_under_root(storage_path) if storage_path else None

    if not storage_path or not Path(abs_path).is_file():
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Stored file not found")
        
    # 3. Loguj publiczne pobieranie (user_id=None, akcja bez uwierzytelnienia)
    await log_action(db, user_id=None, action="download_share", file_id=file_obj.id, details={"share_id": share_id})

    # 4. Zwróć plik
    filename = file_obj.filename
    return FileResponse(path=str(abs_path), filename=filename, media_type="application/octet-stream")