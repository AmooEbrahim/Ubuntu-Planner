"""Day memory API endpoints."""
from datetime import date as date_type, timedelta
from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.schemas.day_memory import (
    DayMemoryPair,
    DayMemoryResponse,
    DayMemoryUpsert,
)
from app.services.day_memory_service import DayMemoryService


router = APIRouter(prefix="/api/day-memory", tags=["day-memory"])


def get_service(db: Session = Depends(get_db)) -> DayMemoryService:
    return DayMemoryService(db)


def _pair_from_rows(target_date: date_type, user_row, ai_row) -> DayMemoryPair:
    return DayMemoryPair(
        date=target_date,
        user=DayMemoryResponse.model_validate(user_row) if user_row else None,
        ai=DayMemoryResponse.model_validate(ai_row) if ai_row else None,
    )


@router.get("/today", response_model=DayMemoryPair)
async def get_today(service: DayMemoryService = Depends(get_service)) -> DayMemoryPair:
    """Get both tracks for today (server-local date)."""
    today = date_type.today()
    user_row, ai_row = service.get_pair(today)
    return _pair_from_rows(today, user_row, ai_row)


@router.get("/range", response_model=List[DayMemoryResponse])
async def list_range(
    start: date_type = Query(...),
    end: date_type = Query(...),
    service: DayMemoryService = Depends(get_service),
):
    """List memory rows between ``start`` and ``end`` inclusive."""
    if end < start:
        raise HTTPException(status_code=400, detail="end must be on or after start")
    if (end - start) > timedelta(days=366):
        raise HTTPException(status_code=400, detail="range cannot exceed 366 days")
    return service.list_range(start, end)


@router.get("/{target_date}", response_model=DayMemoryPair)
async def get_for_date(
    target_date: date_type,
    service: DayMemoryService = Depends(get_service),
) -> DayMemoryPair:
    """Get both tracks for a specific date."""
    user_row, ai_row = service.get_pair(target_date)
    return _pair_from_rows(target_date, user_row, ai_row)


@router.put("/{target_date}", response_model=DayMemoryResponse)
async def upsert_user_track(
    target_date: date_type,
    data: DayMemoryUpsert,
    service: DayMemoryService = Depends(get_service),
):
    """Upsert the user's own track for ``target_date``."""
    return service.upsert(target_date, is_ai=False, data=data.model_dump(exclude_unset=True))


@router.put("/{target_date}/ai", response_model=DayMemoryResponse)
async def upsert_ai_track(
    target_date: date_type,
    data: DayMemoryUpsert,
    service: DayMemoryService = Depends(get_service),
):
    """Upsert the AI's track for ``target_date``.

    This endpoint is exposed for completeness; the AI agent normally writes to
    its track via the ``upsert_day_memory_ai_track`` tool, which calls into the
    same service.
    """
    return service.upsert(target_date, is_ai=True, data=data.model_dump(exclude_unset=True))


@router.delete("/{target_date}", status_code=204)
async def delete_user_track(
    target_date: date_type,
    service: DayMemoryService = Depends(get_service),
):
    """Delete the user's track for ``target_date``."""
    if not service.delete(target_date, is_ai=False):
        raise HTTPException(status_code=404, detail="Day memory not found")


@router.delete("/{target_date}/ai", status_code=204)
async def delete_ai_track(
    target_date: date_type,
    service: DayMemoryService = Depends(get_service),
):
    """Delete the AI's track for ``target_date``."""
    if not service.delete(target_date, is_ai=True):
        raise HTTPException(status_code=404, detail="AI day memory not found")
