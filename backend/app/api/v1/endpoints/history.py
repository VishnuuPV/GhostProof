from __future__ import annotations

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.repositories.scan_repository import ScanRepository
from app.schemas.history import ScanHistoryItem

router = APIRouter()


@router.get("/history", response_model=list[ScanHistoryItem])
async def history(
    limit: int = Query(default=25, ge=1, le=100),
    db: Session = Depends(get_db),
) -> list[ScanHistoryItem]:
    return ScanRepository(db).recent(limit=limit)
