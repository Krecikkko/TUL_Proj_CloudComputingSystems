from typing import Optional, Dict, Any
from datetime import datetime
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.log_book import LogBook

async def log_action(
    db: AsyncSession,
    user_id: Optional[int],
    action: str,
    file_id: Optional[int] = None,
    details: Optional[Dict[str, Any]] = None,
    ip_address: Optional[str] = None,
    timestamp: Optional[datetime] = None,
) -> LogBook:
    entry = LogBook(
        user_id=user_id,
        action=action,
        file_id=file_id,
        details=details or {},
        ip_address=ip_address,
        timestamp=timestamp or datetime.utcnow(),
    )
    db.add(entry)
    await db.commit()
    await db.refresh(entry)
    return entry
