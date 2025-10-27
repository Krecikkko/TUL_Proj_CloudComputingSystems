from fastapi import APIRouter, Depends, File

router = APIRouter(prefix="/api")

@router.get("/file")
def getFile():
    return {"file": "yourfile"}

@router.get("/upload")
def upload():
    return {"upload": "upload file here"}