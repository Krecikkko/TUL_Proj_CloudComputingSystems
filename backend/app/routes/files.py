from fastapi import APIRouter, Depends, UploadFile, File as FileParam, HTTPException, status, Request
from fastapi.responses import FileResponse, JSONResponse
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, desc, asc, String
from sqlalchemy.orm import selectinload
from pathlib import Path
from typing import Optional

from ..db import get_session
from ..models.file import File, User
from ..models.file_version import FileVersion
from ..storage import build_rel_path, save_upload_stream, _abs_under_root
from ..utils.permissions import assert_user_can_delete, assert_user_can_download
from ..utils.auth_deps import get_current_user
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
# async def get_current_user_id(session: AsyncSession = Depends(get_session)) -> int:
#     user = (await session.execute(select(User).where(User.id == 1))).scalars().first()
#     if not user:
#         user = User(id=1, username="user", email="mock@example.com", hashed_password="password", role="admin")
#         session.add(user)
#         await session.commit()
#     return 1

@router.get("/files")
async def list_files(
    session: AsyncSession = Depends(get_session),
    current_user: User = Depends(get_current_user),
    search: Optional[str] = None, # query parameter for filtering
    sort: str = "date_desc",
):
    # Base query: only files belonging to the authenticated user
    q = select(File).where(File.uploaded_by == current_user.id)
    
    # 1. Add Search/Filter logic
    if search:
        # Use ilike for case-insensitive partial match on filename
        q = q.where(File.filename.ilike(f"%{search}%"))

    # 2. Add Sort/Order logic
    if sort == "date_desc":
        # Default: newest first
        q = q.order_by(File.uploaded_at.desc())
    elif sort == "date_asc":
        q = q.order_by(File.uploaded_at.asc())
    elif sort == "name_asc":
        # Cast to String to ensure correct alphabetical sort for all database backends
        q = q.order_by(File.filename.cast(String).asc())
    elif sort == "name_desc":
        q = q.order_by(File.filename.cast(String).desc())
    else:
        # Handle invalid sort parameter
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid sort parameter: {sort}. Must be one of date_desc, date_asc, name_asc, name_desc."
        )

    result = await session.execute(q)
    rows = result.scalars().all()
    
    return [
        {
            "id": r.id,
            "filename": r.filename,
            "size": r.size,
            "uploaded_at": r.uploaded_at.isoformat() if r.uploaded_at else None,
        }
        for r in rows
    ]

@router.get("/files/{file_id}/info", summary="Get file metadata and version count")
async def get_file_info(
    file_id: int,
    session: AsyncSession = Depends(get_session),
    current_user: User = Depends(get_current_user)
):
    # Authorization check 
    _ = await assert_user_can_download(session, current_user, file_id) 
    # Fetch the file
    q = select(File).where(File.id == file_id).options(
        selectinload(File.uploader),
        selectinload(File.versions)
    )
    result = await session.execute(q)
    file_with_rels = result.scalars().first()

    if not file_with_rels:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="File not found")
    
    version_count = len(file_with_rels.versions)

    return {
        "id": file_with_rels.id,
        "filename": file_with_rels.filename,
        "size": file_with_rels.size if file_with_rels.size is not None else 0,
        "uploaded_at": file_with_rels.uploaded_at.isoformat() if file_with_rels.uploaded_at else None,
        "owner": file_with_rels.uploader.username if file_with_rels.uploader else "Unknown",
        "versions": version_count
    }

@router.post("/upload")
async def upload(
    request: Request,
    file: UploadFile = FileParam(...),
    session: AsyncSession = Depends(get_session),
    current_user: User = Depends(get_current_user),
):
    if not file.filename:
        raise HTTPException(400, "missing filename")
    
    # size validation
    validate_file_size(file)

    # 1) Create file record (na razie puste filepath/size – uzupełnimy po zapisie)
    f = File(
        filename=file.filename,
        filepath="",
        size=None,
        uploaded_by=current_user.id,
    )
    session.add(f)
    await session.flush()  # nada id

    # 2) Save file to the disk
    rel_path = build_rel_path(current_user.id, f.id, file.filename)
    size = await save_upload_stream(file, rel_path)

    # 3) Update file record
    f.filepath = rel_path
    f.size = size
    await session.commit()

    # 4) Create FileVersion (version_number = 1 dla nowego pliku)
    v = FileVersion(
        file_id=f.id,
        version_number=1,
        filepath=rel_path,
        size=size,
        notes=None,  # jeśli chcesz dodać opis – przekaż z requestu
    )
    session.add(v)
    await session.commit()

    # 5) Log upload (z IP)
    client_ip = request.client.host if request.client else None
    await log_action(session, user_id=current_user.id, action="upload", file_id=f.id, details={"size": size}, ip_address=client_ip)

    return {"file_id": f.id, "filename": f.filename, "size": size}

def resolve_current_storage_path(file_obj) -> Optional[str]:
    # preferuj główny filepath
    if getattr(file_obj, "filepath", None):
        return file_obj.filepath
    # w razie czego — weź najwyższy version_number
    versions = getattr(file_obj, "versions", [])
    if versions:
        return sorted(versions, key=lambda v: v.version_number)[-1].filepath
    return None

@router.get("/download/{file_id}")
async def download_file(
    file_id: int,
    request: Request,
    session: AsyncSession = Depends(get_session),
    current_user: User = Depends(get_current_user)
):
    file_obj = await assert_user_can_download(session, current_user, file_id)
    storage_path = resolve_current_storage_path(file_obj)
    abs_path = _abs_under_root(storage_path) if storage_path else None

    if not storage_path or not Path(abs_path).is_file():
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Stored file not found")

    # log download
    client_ip = request.client.host if request.client else None
    await log_action(session, user_id=current_user.id, action="download", file_id=file_id, details={"path": str(abs_path)}, ip_address=client_ip)

    # użyj nazwy z modelu File
    filename = getattr(file_obj, "filename", Path(abs_path).name)
    return FileResponse(path=str(abs_path), filename=filename, media_type="application/octet-stream")

@router.delete("/delete/{file_id}")
async def delete_file(
    file_id: int,
    request: Request,
    session: AsyncSession = Depends(get_session),
    current_user: User = Depends(get_current_user)
):
    file_obj = await assert_user_can_delete(session, current_user, file_id)
    storage_path = resolve_current_storage_path(file_obj)
    abs_path = _abs_under_root(storage_path) if storage_path else None

    # Remove physical file if exists
    if storage_path:
        try:
            p = Path(abs_path)
            if p.exists():
                p.unlink()
        except Exception as e:
            client_ip = request.client.host if request.client else None
            await log_action(session, user_id=current_user.id, action="delete_error", file_id=file_id, details={"error": str(e)}, ip_address=client_ip)

    # Remove DB record
    await session.delete(file_obj)
    await session.commit()

    # log delete
    client_ip = request.client.host if request.client else None
    await log_action(session, user_id=current_user.id, action="delete", file_id=file_id, ip_address=client_ip)

    return JSONResponse({"message": "File deleted successfully"}, status_code=status.HTTP_200_OK)
