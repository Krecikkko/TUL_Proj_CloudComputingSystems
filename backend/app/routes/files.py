from fastapi import APIRouter, Depends, UploadFile, File as FileParam, HTTPException, status, Request
from fastapi.responses import FileResponse, JSONResponse
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, desc, asc, String
from sqlalchemy.orm import selectinload
from pathlib import Path
from typing import Optional
from uuid import uuid4

from ..db import get_session
from ..models.file import File, User
from ..models.file_version import FileVersion
from ..storage import build_rel_path, save_upload_stream, _abs_under_root
from ..utils.permissions import assert_user_can_delete, assert_user_can_download
from ..utils.auth_deps import get_current_user
from app.utils.logging import log_action
from app.core.constants import MAX_UPLOAD_BYTES
from app.schemas.file import DeleteBatchIn

router = APIRouter(prefix="/api", tags=["Files"])

def validate_file_size(file_obj) -> None:
    file_obj.file.seek(0, 2)
    size = file_obj.file.tell()
    file_obj.file.seek(0)
    if size > MAX_UPLOAD_BYTES:
        raise HTTPException(
            status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
            detail="File exceeds 100MB limit"
        )

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
    notes: Optional[str] = None
):
    if not file.filename:
        raise HTTPException(400, "missing filename")
    
    validate_file_size(file)

    client_ip = request.client.host if request.client else None

    # 1. Określ ID i wersję (dla ścieżki zapisu)
    existing_file_res = await session.execute(
        select(File)
        .where(File.uploaded_by == current_user.id)
        .where(File.filename == file.filename)
    )
    existing_file = existing_file_res.scalars().first()

    if not existing_file:
        f = File(filename=file.filename, filepath="", size=None, uploaded_by=current_user.id, current_version=1)
        session.add(f)
        await session.flush()
        file_id = f.id
        initial_version = 1
    else:
        file_id = existing_file.id
        versions_res = await session.execute(
            select(func.max(FileVersion.version_number)).where(FileVersion.file_id == file_id)
        )
        max_version = versions_res.scalar_one_or_none()
        initial_version = (max_version if max_version is not None else existing_file.current_version or 0) + 1

    # 2. Zapisz plik tymczasowo, aby uzyskać rozmiar i hash
    temp_rel_path = build_rel_path(current_user.id, file_id, file.filename, initial_version)
    size, checksum = await save_upload_stream(file, temp_rel_path) # Używamy nowej funkcji z checksum

    # 3. Sprawdzenie de-duplikacji
    duplicate_res = await session.execute(
        select(FileVersion).where(FileVersion.checksum == checksum)
    )
    duplicate_version = duplicate_res.scalars().first()
    
    if duplicate_version:
        # Znaleziono duplikat: usuń plik i użyj ścieżki duplikatu
        Path(_abs_under_root(temp_rel_path)).unlink(missing_ok=True)
        final_rel_path = duplicate_version.filepath
        final_size = duplicate_version.size
    else:
        # Brak duplikatu: użyj nowo przesłanego pliku
        final_rel_path = temp_rel_path
        final_size = size

    # 4. Zapisz/Aktualizuj rekordy w DB
    
    if existing_file:
        # Aktualizacja istniejącego pliku
        existing_file.filepath = final_rel_path
        existing_file.size = final_size
        existing_file.current_version = initial_version

        v = FileVersion(
            file_id=file_id, version_number=initial_version, filepath=final_rel_path, size=final_size, notes=notes, checksum=checksum
        )
        session.add(v)
        await session.commit()
        
        log_details = {"size": final_size, "version": initial_version, "duplicate": bool(duplicate_version)}
        await log_action(session, user_id=current_user.id, action="upload", file_id=file_id, details=log_details, ip_address=client_ip)
        
        return {"file_id": file_id, "filename": existing_file.filename, "size": final_size, "version": initial_version, "message": f"New version uploaded ({'deduplicated' if duplicate_version else 'new file'})"}

    else:
        # Tworzenie nowego pliku (f już ma ID)
        f.filepath = final_rel_path
        f.size = final_size
        
        v = FileVersion(
            file_id=file_id, version_number=initial_version, filepath=final_rel_path, size=final_size, notes=notes, checksum=checksum
        )
        session.add(v)
        await session.commit()
    
        log_details = {"size": final_size, "version": initial_version, "duplicate": bool(duplicate_version)}
        await log_action(session, user_id=current_user.id, action="upload", file_id=file_id, details=log_details, ip_address=client_ip)
    
        return {"file_id": file_id, "filename": f.filename, "size": final_size, "version": initial_version, "message": f"File created and version 1 uploaded ({'deduplicated' if duplicate_version else 'new file'})"}

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

@router.post("/delete-multiple", status_code=status.HTTP_200_OK, summary="Batch delete files")
async def delete_multiple_files(
    payload: DeleteBatchIn,
    request: Request,
    session: AsyncSession = Depends(get_session),
    current_user: User = Depends(get_current_user)
):
    if not payload.file_ids:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="File IDs list cannot be empty")

    deleted_count = 0
    failed_ids = []
    
    # Przetwarzaj unikalne ID
    for file_id in set(payload.file_ids): 
        try:
            # Użyj istniejącej logiki autoryzacji (tylko właściciel/admin)
            file_obj = await assert_user_can_delete(session, current_user, file_id)

            # Usuwanie pliku fizycznego (reuse logic from delete_file)
            storage_path = resolve_current_storage_path(file_obj)
            abs_path = _abs_under_root(storage_path) if storage_path else None
            
            if storage_path:
                try:
                    p = Path(abs_path)
                    if p.exists():
                        p.unlink()
                except Exception as e:
                    # Loguj błąd, ale kontynuuj usuwanie z DB
                    client_ip = request.client.host if request.client else None
                    await log_action(session, user_id=current_user.id, action="delete_error", file_id=file_id, details={"error": str(e), "batch": True}, ip_address=client_ip)
            
            # Usuń rekord z DB (cascade delete usunie też FileVersions)
            await session.delete(file_obj)
            await session.commit()
            
            # Loguj udane usunięcie
            client_ip = request.client.host if request.client else None
            await log_action(session, user_id=current_user.id, action="delete", file_id=file_id, details={"batch": True}, ip_address=client_ip)
            
            deleted_count += 1
            
        except HTTPException as e:
            # Błąd autoryzacji lub 404
            failed_ids.append({"id": file_id, "detail": e.detail})
        except Exception as e:
            failed_ids.append({"id": file_id, "detail": f"Internal server error: {str(e)}"})


    if deleted_count == 0 and failed_ids:
        # Jeśli lista nie była pusta, ale nie udało się usunąć żadnego pliku
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Failed to delete any files. Check details.",
            headers={"X-Failed-Deletes": str([f['id'] for f in failed_ids])} # Zwróć tylko ID
        )
    
    return {
        "message": f"Successfully deleted {deleted_count} files.",
        "deleted_count": deleted_count,
        "failed_to_delete": failed_ids
    }

@router.post("/files/{file_id}/share", summary="Generate or retrieve a sharing link for a file")
async def generate_share_link(
    file_id: int,
    session: AsyncSession = Depends(get_session),
    current_user: User = Depends(get_current_user)
):
    # Ograniczone do właściciela (używając assert_user_can_delete, który sprawdza własność)
    file_obj = await assert_user_can_delete(session, current_user, file_id)

    if not file_obj.share_link_id:
        file_obj.share_link_id = str(uuid4())
        await session.commit()
        await session.refresh(file_obj)
        
        await log_action(session, user_id=current_user.id, action="share_create", file_id=file_id)

    # Zwróć ścieżkę do publicznego endpointu
    share_url = f"/share/{file_obj.share_link_id}" 

    return {"message": "Share link generated/retrieved", "share_id": file_obj.share_link_id, "share_url": share_url}