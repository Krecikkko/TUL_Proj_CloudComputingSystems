from pydantic import BaseModel, datetime

class FileInfoOut(BaseModel):
    id: int
    filename: str
    size: int
    uploaded_at: datetime
    owner: str
    versions: int

    class Config:
        from_attributes = True