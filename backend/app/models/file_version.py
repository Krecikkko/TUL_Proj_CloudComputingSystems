from datetime import datetime
from sqlalchemy import Column, Integer, String, ForeignKey, DateTime, BigInteger
from sqlalchemy.orm import relationship
from .base import Base

class FileVersion(Base):
    __tablename__ = "file_versions"

    id = Column(Integer, primary_key=True, index=True)
    file_id = Column(Integer, ForeignKey("files.id", ondelete="CASCADE"), nullable=False, index=True)
    version = Column(Integer, nullable=False)
    storage_path = Column(String, nullable=False)
    checksum = Column(String, nullable=True)
    size_bytes = Column(BigInteger, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    file = relationship("File", back_populates="versions")
