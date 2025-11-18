from datetime import datetime
from sqlalchemy import Column, Integer, ForeignKey, String, DateTime, Text, Index
from sqlalchemy.orm import relationship
from .base import Base

class FileVersion(Base):
    __tablename__ = "file_versions"

    id = Column(Integer, primary_key=True, index=True)
    file_id = Column(Integer, ForeignKey("files.id", ondelete="CASCADE"), nullable=False, index=True)
    version_number = Column(Integer, nullable=False)
    filepath = Column(String(255), nullable=False)
    size = Column(Integer, nullable=True)
    uploaded_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    notes = Column(Text, nullable=True)

    file = relationship("File", back_populates="versions")

    __table_args__ = ( Index('idx_file_version', 'file_id', 'version_number'),)
