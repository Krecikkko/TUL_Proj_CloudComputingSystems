from fastapi import APIRouter, Depends, HTTPException, Query, Response, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import func, select, desc
from typing import Optional
import csv
from io import StringIO
from datetime import date, timedelta
from ..db import get_session
from ..models.log_book import LogBook
from ..models.user import User # Dodano import
from ..utils.auth_deps import require_roles # Dodano import

router = APIRouter(prefix="/api/logbook", tags = ["LogBook"])

@router.get("/")
async def get_logbook_entries(
    user_id: Optional[int] = Query(None, description="Filter by user ID"),
    action: Optional[str] = Query(None, description="Filter by action type"),
    start_date: Optional[date] = Query(None, description="Filter by starting date"),
    end_date: Optional[date] = Query(None, description="Filter by ending date"),
    sort_by: str = Query("timestamp_desc", description="Sortt by timestamp"),
    db: AsyncSession = Depends(get_session),
    current_user: User = Depends(require_roles("admin")), # Zabezpieczenie dostępu
):
    query = select(LogBook)

    if user_id is not None:
        query = query.filter(LogBook.user_id == user_id)
    if action:
        query = query.filter(LogBook.action == action)
    if start_date:
        query = query.filter(LogBook.timestamp >= start_date)
    if end_date:
        next_day = end_date + timedelta(days=1)
        query = query.filter(LogBook.timestamp < next_day)

    if sort_by == "timestamp_asc":
        query = query.order_by(LogBook.timestamp.asc())
    else:
        query = query.order_by(desc(LogBook.timestamp))
    
    result = await db.execute(query)
    entries = result.scalars().all()
    
    return[
        {
            "id": entry.id,
            "user_id": entry.user_id,
            "action": entry.action,
            "timestamp": entry.timestamp.isoformat(),
            "file_id": entry.file_id,
            "details": entry.details
        }
        for entry in entries
    ]

@router.get("/stats")
async def get_logbook_stats(
    db: AsyncSession = Depends(get_session),
    current_user: User = Depends(require_roles("admin")), # Zabezpieczenie dostępu
):
    result_action = await db.execute(
        select(LogBook.action, func.count(LogBook.id)).group_by(LogBook.action)
    )
    action_counts = result_action.all()

    stats={f"total_{action}s": count for action, count in action_counts}

    result_users = await db.execute(
        select(func.count(LogBook.user_id.distinct()))
    )
    unique_users = result_users.scalar_one()
    stats["total_unique_users"] = unique_users
    
    return stats

@router.get("/export", response_class=Response, name="export_logbook_to_csv")
async def export_logbook_to_csv(
    db: AsyncSession = Depends(get_session),
    current_user: User = Depends(require_roles("admin")), # Zabezpieczenie dostępu
):
    result = await db.execute(
        select(LogBook).order_by(desc(LogBook.timestamp))
    )
    entries = result.scalars().all()

    if not entries:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="No log entries")
    
    output=StringIO()
    fieldnames = ['id', 'user_id', 'action', 'timestamp', 'file_id', 'details']
    writer = csv.DictWriter(output, fieldnames=fieldnames)
    writer.writeheader()

    for entry in entries:
        writer.writerow({
            'id': entry.id,
            'user_id': entry.user_id,
            'action': entry.action,
            'timestamp': entry.timestamp.isoformat() if entry.timestamp else '',
            'file_id': entry.file_id,
            'details': str(entry.details)
        })
    
    return Response(
        content=output.getvalue(),
        media_type="text/csv",
        headers={"Content-Disposition": "attachment; filename=logbook_export.csv"}
    )