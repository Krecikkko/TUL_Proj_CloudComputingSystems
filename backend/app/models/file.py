from datetime import datatime
from typing import Optional, List
from uuid import UUID, uuid4
from sqlalchemy import (
    String, Boolean, DateTime, Integer, ForeignKey, UniqueConstraint,
    Text, Index, BigInteger, func
)
from sqlalchemy.orm import declarative_base, Mapped, mapped_column, relationship

Base = declarative_base()

# ---------- Mock Users (temporary) ----------
class User(Base):
    __tablename__ = "users"
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    email: Mapped[Optional[str]] = mapped_column(String(255), unique=True)
    created_at: Mapped[DateTime] = mapped_column(DateTime(timezone=True), server_default=func.now())

class File(Base):
    __tablename__ = "file"
    id: Mapped[UUID] = mapped_column(primary_key=True, autoincrement=True)
    filename: Mapped[str] = mapped_column(String(255), nullable=False)
    filepath: Mapped[str] = mapped_column(String(1024), nullable=False)
    size: Mapped[Optional[int]] = mapped_column(Integer)
    uploaded_by: Mapped[Optional[int]] = mapped_column(ForeignKey("users.id"))
    uploaded_at: Mapped[DateTime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    current_version: Mapped[Optional[int]] = mapped_column(Integer)

    # relationships
    versions: Mapped[List["FileVersion"]] = relationship(
        back_populates="file",
        cascade="all, delete-orphan",
        order_by="FileVersion.version_number",
    )
    uploader: Mapped[Optional[User]] = relationship()

    __table_args__ = (
        # Helpful for list views by newest file first
        Index("ix_files_uploaded_at_desc", uploaded_at.desc()),
    )

class FileVersion(Base):
    __tablename__ = "file_versions"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    file_id: Mapped[int] = mapped_column(ForeignKey("files.id", ondelete="CASCADE"), index=True)
    version_number: Mapped[int] = mapped_column(Integer, nullable=False)
    filepath: Mapped[str] = mapped_column(String(1024), nullable=False)
    size: Mapped[Optional[int]] = mapped_column(BigInteger)
    uploaded_at: Mapped[DateTime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    notes: Mapped[Optional[str]] = mapped_column(Text)

    file: Mapped[File] = relationship(back_populates="versions")

    __table_args__ = (
        # One version N per file
        UniqueConstraint("file_id", "version_number", name="uq_file_version_per_file"),
        Index("ix_file_versions_created_desc", uploaded_at.desc()),
    )