import os
from fastapi import APIRouter, Depends, HTTPException, Response, status, BackgroundTasks
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select 
from typing import List, Optional
from zipfile import ZipFile, ZIP_DEFLATED
from io import BytesIO
from ..db import get_session 
from ..models.file_version import FileVersion 
from ..models.file import File
from ..models.user import User
from ..utils.logging import log_action
from ..utils.auth_deps import get_current_user
from ..utils.permissions import assert_user_can_download, assert_user_can_delete
from ..schemas.file import DeleteBatchIn
from ..storage import _abs_under_root

router = APIRouter(prefix="/api/files", tags = ["File versions"])

@router.get("/{file_id}/versions")
async def list_file_versions(
    file_id: int, 
    db: AsyncSession = Depends(get_session),
    current_user: User = Depends(get_current_user) # Zabezpieczenie dostępu
): 
    # Autoryzacja: Weryfikacja dostępu do odczytu (właściciel lub współdzielony)
    _ = await assert_user_can_download(db, current_user, file_id)

    result = await db.execute(
        select(FileVersion).where(FileVersion.file_id == file_id).order_by(FileVersion.version_number) 
    )
    versions = result.scalars().all()
    
    if not versions:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Versions not found for this file")

    return [
        {
            "version": v.version_number, 
            "size": v.size, 
            "uploaded_at": v.uploaded_at.isoformat() if v.uploaded_at else None,
            "filepath": v.filepath,
            "notes": v.notes
        } 
        for v in versions
    ]

def resolve_current_storage_path(file_obj) -> Optional[str]:
    if getattr(file_obj, "filepath", None):
        return file_obj.filepath
    versions = getattr(file_obj, "versions", [])
    if versions:
        return sorted(versions, key=lambda v: v.version_number)[-1].filepath
    return None

@router.post("/download-zip")
async def download_zip(
    payload: DeleteBatchIn, # Changed from file_id: List[int] to match JSON body { "file_ids": ... }
    db: AsyncSession = Depends(get_session),
    current_user: User = Depends(get_current_user)
):
    files_to_zip = []
    
    # payload.file_ids comes from the schema
    for f_id in payload.file_ids:
        try:
            # We need to load versions to resolve the path if it's not on the main object
            file_obj = await assert_user_can_download(db, current_user, f_id)
            
            # Explicitly load versions if they aren't loaded, 
            # though assert_user_can_download usually returns the File model.
            # Depending on your lazy loading settings, you might need to ensure they are present
            # if resolving path relies on them.
            
            files_to_zip.append(file_obj)
        except HTTPException as e:
            if e.status_code == status.HTTP_404_NOT_FOUND:
                continue 
            if e.status_code == status.HTTP_403_FORBIDDEN:
                raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=f"Permission denied for file ID: {f_id}")
            raise e

    if not files_to_zip:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="No authorized files found for the given IDs")
    
    zbuffer = BytesIO()
    # Use ZIP_DEFLATED for compression
    with ZipFile(zbuffer, 'w', ZIP_DEFLATED) as zip_file:
        for file_obj in files_to_zip:
            try:
                # 1. Resolve the physical path
                storage_path = resolve_current_storage_path(file_obj)
                if not storage_path:
                    print(f"Skipping {file_obj.filename}: No storage path found")
                    continue

                abs_path = _abs_under_root(storage_path)
                
                # 2. Check if file exists on disk
                if not os.path.exists(abs_path):
                    print(f"Skipping {file_obj.filename}: File not found at {abs_path}")
                    continue

                # 3. Write actual file content to zip
                # arcname ensures the file in the zip has the correct logical filename
                zip_file.write(abs_path, arcname=file_obj.filename)
                
                await log_action(db, user_id=current_user.id, action='download', file_id=file_obj.id, details={"zip_part": True})
            except Exception as e:
                print(f"Error during archiving file {file_obj.filename}: {e}")
                
    zbuffer.seek(0)

    return Response(
        content=zbuffer.read(),
        media_type="application/zip",
        headers={"Content-Disposition": "attachment; filename=files_download.zip"}
    )
    

@router.post("/{file_id}/rollback/{version_number}")
async def rollback_file_version(
    file_id: int, 
    version_number: int, 
    db: AsyncSession = Depends(get_session),
    current_user: User = Depends(get_current_user) # Zabezpieczenie dostępu
):
    # Autoryzacja: Rollback wymaga uprawnień właściciela, co weryfikuje assert_user_can_delete
    cur_file = await assert_user_can_delete(db, current_user, file_id) # Zwraca obiekt File

    result_ver = await db.execute(
        select(FileVersion).where(
            (FileVersion.file_id == file_id) & (FileVersion.version_number == version_number)
        )
    )
    target_ver = result_ver.scalar_one_or_none()

    if not target_ver:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Version not found")
    
    cur_file.filepath = target_ver.filepath
    cur_file.size = target_ver.size
    cur_file.current_version = target_ver.version_number
    
    await db.commit()
    await log_action(db, user_id=current_user.id, action="rollback", file_id=file_id, details={"rolled_back_to": version_number})

    return {"message": f"File {file_id} rolled back to version {version_number}"}