from fastapi import APIRouter, Depends, UploadFile, File as FileParam, HTTPException, status
from fastapi.responses import FileResponse, JSONResponse
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import Session
from sqlalchemy import select
from pathlib import Path
from typing import Optional
from ..db import get_session
from ..models.file import File, User
from ..storage import build_rel_path, save_upload_stream, _abs_under_root
from ..utils.permissions import assert_user_can_delete, assert_user_can_download
from app.utils.logging import log_action
from app.core.constants import MAX_UPLOAD_BYTES

router = APIRouter(prefix="/api")

def validate_file_size(file_obj) -> None:
    file_obj.file.seek(0, 2)
    size = file_obj.file.tell()
    file_obj.file.seek(0)
    if size > MAX_UPLOAD_BYTES:
        raise HTTPException(
            status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
            detail="File exceeds 100MB limit"
        )

# Mock "auth": we consider user_id = 1 and we create it if it doesnt exist
async def get_current_user_id(session: AsyncSession = Depends(get_session)) -> int:
    user = (await session.execute(select(User).where(User.id == 1))).scalars().first()
    if not user:
        user = User(id=1, username="user", email="mock@example.com", password_hash="password", role="admin")
        session.add(user)
        await session.commit()
    return 1

@router.get("/files")
async def list_files(
    session: AsyncSession = Depends(get_session),
    user_id: int = Depends(get_current_user_id),
):
    q = await session.execute(
        select(File).where(File.uploaded_by == user_id).order_by(File.uploaded_at.desc())
    )
    rows = q.scalars().all()
    return [
        {
            "id": r.id,
            "filename": r.filename,
            "size": r.size,
            "uploaded_at": r.uploaded_at.isoformat() if r.uploaded_at else None,
        }
        for r in rows
    ]

@router.post("/upload")
async def upload(
    file: UploadFile = FileParam(...),
    session: AsyncSession = Depends(get_session),
    user_id: int = Depends(get_current_user_id),
):
    if not file.filename:
        raise HTTPException(400, "missing filename")
    
    # Check if the file fullfils the constrains
    validate_file_size(file)

    # 1) Create file record
    f = File(
        filename=file.filename,
        filepath="",   # We fill it after saving to the disk
        size=None,
        uploaded_by=user_id,
    )
    session.add(f)
    await session.flush()  # It assigns id

    # 2) Save file to the disk
    rel_path = build_rel_path(user_id, f.id, file.filename)
    size = await save_upload_stream(file, rel_path)

    # 3) Update file record
    f.filepath = rel_path
    f.size = size
    await session.commit()

    return {"file_id": f.id, "filename": f.filename, "size": size}

def resolve_current_storage_path(file_obj) -> Optional[str]:
    if getattr(file_obj, "filepath", None):
        return file_obj.filepath
    versions = getattr(file_obj, "versions", [])
    if versions:
        return sorted(versions, key=lambda v: v.version)[-1].filepath
    return None

@router.get("/download/{file_id}")
async def download_file(file_id: int, db: Session = Depends(get_session), user_id: int = Depends(get_current_user_id)):
    file_obj = await assert_user_can_download(db, user_id, file_id)
    storage_path = resolve_current_storage_path(file_obj)
    # Convert relative filepath to absolute
    abs_path = _abs_under_root(storage_path)

    if not storage_path or not Path(abs_path).is_file():
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Stored file not found")

    # log download
    log_action(db, user_id=user_id, action="download", file_id=file_id, details={"path": abs_path})

    # FileResponse autmatically set headers Content-Disposition
    filename = getattr(file_obj, "original_name", Path(abs_path).name)
    return FileResponse(path=abs_path, filename=filename, media_type="application/octet-stream")

@router.delete("/delete/{file_id}")
async def delete_file(file_id: int, db: Session = Depends(get_session), user_id: int = Depends(get_current_user_id)):
    file_obj = await assert_user_can_delete(db, user_id, file_id)
    storage_path = resolve_current_storage_path(file_obj)
    # Convert relative filepath to absolute
    abs_path = _abs_under_root(storage_path)

    # Remove physical file if exists
    if storage_path:
        try:
            p = Path(abs_path)
            if p.exists():
                p.unlink()
        except Exception as e:
            # Log error
            log_action(db, user_id=user_id, action="delete_error", file_id=file_id, details={"error": str(e)})

    # Remove version records
    await db.delete(file_obj)
    await db.commit()

    # log delete
    await log_action(db, user_id=user_id, action="delete", file_id=file_id)

    return JSONResponse({"message": "File deleted successfully"}, status_code=status.HTTP_200_OK)