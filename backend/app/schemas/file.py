from pydantic import BaseModel
from datetime import datetime
from typing import List

class FileInfoOut(BaseModel):
    id: int
    filename: str
    size: int
    uploaded_at: datetime
    owner: str
    versions: int

    class Config:
        from_attributes = True

class DeleteBatchIn(BaseModel):
    file_ids: List[int]
