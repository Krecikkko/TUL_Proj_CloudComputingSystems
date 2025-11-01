from fastapi import APIRouter, Depends, UploadFile, File as FileParam, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from ..db import get_session
from ..models.file import File, User
from ..storage import build_rel_path, save_upload_stream

router = APIRouter(prefix="/api")

# Mock "auth": we consider user_id = 1 and we create it if it doesnt exist
async def get_current_user_id(session: AsyncSession = Depends(get_session)) -> int:
    user = (await session.execute(select(User).where(User.id == 1))).scalars().first()
    if not user:
        user = User(id=1, email="mock@example.com")
        session.add(user)
        await session.commit()
    return 1

@router.post("/upload")
async def upload(
    file: UploadFile = FileParam(...),
    session: AsyncSession = Depends(get_session),
    user_id: int = Depends(get_current_user_id),
):
    if not file.filename:
        raise HTTPException(400, "missing filename")

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