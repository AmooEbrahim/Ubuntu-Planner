"""Statistics API endpoints."""

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from datetime import date
from typing import Dict, List
from app.core.database import get_db
from app.services.statistics_service import StatisticsService


router = APIRouter(prefix="/api/statistics", tags=["statistics"])


def get_service(db: Session = Depends(get_db)) -> StatisticsService:
    """Get statistics service instance.

    Args:
        db: Database session

    Returns:
        StatisticsService instance
    """
    return StatisticsService(db)


@router.get("/overview")
def get_overview(
    start_date: date = Query(None),
    end_date: date = Query(None),
    service: StatisticsService = Depends(get_service)
) -> Dict[str, int | float]:
    """Get overview statistics.

    Returns total sessions, total minutes worked, and average satisfaction score
    for the specified date range.
    """
    return service.get_overview(start_date=start_date, end_date=end_date)


@router.get("/by-project")
def get_by_project(
    start_date: date = Query(None),
    end_date: date = Query(None),
    service: StatisticsService = Depends(get_service)
) -> List[Dict]:
    """Get time spent per project.

    Returns session count and total minutes for each project
    in the specified date range.
    """
    return service.get_by_project(start_date=start_date, end_date=end_date)


@router.get("/daily-activity")
def get_daily_activity(
    start_date: date = Query(None),
    end_date: date = Query(None),
    service: StatisticsService = Depends(get_service)
) -> List[Dict]:
    """Get daily activity summary.

    Returns daily session count, total minutes, and average satisfaction
    for the specified date range.
    """
    return service.get_daily_activity(start_date=start_date, end_date=end_date)


@router.get("/by-tag")
def get_by_tag(
    start_date: date = Query(None),
    end_date: date = Query(None),
    service: StatisticsService = Depends(get_service)
) -> List[Dict]:
    """Get time spent per tag.

    Returns session count and total minutes for each tag
    in the specified date range.
    """
    return service.get_by_tag(start_date=start_date, end_date=end_date)