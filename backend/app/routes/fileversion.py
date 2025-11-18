from fastapi import APIRouter, Depends, HTTPException, Response, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select 
from typing import List
from zipfile import ZipFile
from io import BytesIO
from ..db import get_session 
from ..models.file_version import FileVersion 
from ..models.file import File
from ..models.user import User # Dodano import
from ..utils.logging import log_action
from ..utils.auth_deps import get_current_user # Dodano import
from ..utils.permissions import assert_user_can_download, assert_user_can_delete # Dodano import

router = APIRouter(prefix="/api/files", tags = ["File versions"])

@router.get("/{file_id}/versions")
async def list_file_versions(
    file_id: int, 
    db: AsyncSession = Depends(get_session),
    current_user: User = Depends(get_current_user) # Zabezpieczenie dostępu
): 
    # Autoryzacja: Weryfikacja dostępu do odczytu (właściciel lub współdzielony)
    _ = await assert_user_can_download(db, current_user.id, file_id)

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

@router.post("/download-zip")
async def download_zip(
    file_id: List[int], # Lista ID plików do pobrania
    db: AsyncSession = Depends(get_session),
    current_user: User = Depends(get_current_user) # Zabezpieczenie dostępu
):
    files_to_zip = []
    
    # Weryfikacja dostępu dla każdego pliku w liście
    for f_id in file_id:
        try:
            file_obj = await assert_user_can_download(db, current_user.id, f_id)
            files_to_zip.append(file_obj)
        except HTTPException as e:
            if e.status_code == status.HTTP_404_NOT_FOUND:
                continue # Pomijamy pliki, których nie znaleziono
            if e.status_code == status.HTTP_403_FORBIDDEN:
                # W przypadku braku uprawnień do któregoś pliku, rzucamy błąd
                raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=f"Permission denied for file ID: {f_id}")
            raise e


    if not files_to_zip:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="No authorized files found for the given IDs")
    
    zbuffer = BytesIO()
    with ZipFile(zbuffer, 'w') as zip_file:
        for file_obj in files_to_zip:
            try:
                mock = f"Content of file {file_obj.filename} with version: {file_obj.current_version})"
                zip_file.writestr(file_obj.filename, mock)
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
    cur_file = await assert_user_can_delete(db, current_user.id, file_id) # Zwraca obiekt File

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