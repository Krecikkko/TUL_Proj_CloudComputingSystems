from datetime import datetime
from typing import Optional, List
from uuid import UUID, uuid4
from sqlalchemy import (
    String, Boolean, DateTime, Integer, ForeignKey, UniqueConstraint,
    Text, Index, BigInteger, func
)
from sqlalchemy.orm import declarative_base, Mapped, mapped_column, relationship
from .base import Base
from .user import User
from .file_version import FileVersion

class File(Base):
    __tablename__ = "files"
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    filename: Mapped[str] = mapped_column(String(255), nullable=False)
    filepath: Mapped[str] = mapped_column(String(1024), nullable=False)
    size: Mapped[Optional[int]] = mapped_column(Integer)
    uploaded_by: Mapped[Optional[int]] = mapped_column(ForeignKey("users.id"))
    uploaded_at: Mapped[DateTime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    current_version: Mapped[Optional[int]] = mapped_column(Integer)
    uploader: Mapped[Optional[User]] = relationship()

    __table_args__ = (
        # Helpful for list views by newest file first
        Index("ix_files_uploaded_at_desc", uploaded_at.desc()),
    )

    versions = relationship("FileVersion", back_populates="file", cascade="all, delete-orphan", order_by="FileVersion.version")