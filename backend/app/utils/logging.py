from typing import Optional, Dict, Any
from sqlalchemy.orm import Session
from app.models.log_book import LogBook

def log_action(db: Session, user_id: Optional[int], action: str, file_id: Optional[int] = None, details: Optional[Dict[str, Any]] = None) -> LogBook:
    """
    Saved by other modules:
      from app.utils.logging import log_action
      log_action(db, user_id=1, action="upload", file_id=5, details={"size": 1024})
      log_action(db, user_id=1, action="login", details={"ip": "192.168.1.1"})
    """
    entry = LogBook(user_id=user_id, action=action, file_id=file_id, details=details or {})
    db.add(entry)
    db.commit()
    db.refresh(entry)
    return entry
