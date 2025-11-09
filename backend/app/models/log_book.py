from datetime import datetime
from sqlalchemy import Column, Integer, ForeignKey, String, DateTime, JSON, CheckConstraint
from sqlalchemy.orm import relationship
from .base import Base  # dostosuj import

class LogBook(Base):
    __tablename__ = "log_book"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="SET NULL"), nullable=True, index=True)
    action = Column(String, nullable=False)  # "login","logout","upload","download","delete"
    file_id = Column(Integer, ForeignKey("files.id", ondelete="SET NULL"), nullable=True, index=True)
    timestamp = Column(DateTime, default=datetime.utcnow, nullable=False)
    ip_address = Column(String, nullable=True)
    details = Column(JSON, nullable=True)

    __table_args__ = (
        CheckConstraint(
            "action in ('login','logout','upload','download','delete')",
            name="ck_log_book_action"
        ),
    )

    user = relationship("User", lazy="joined")
    file = relationship("File", lazy="joined")
