"""Statistics API endpoints."""

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from sqlalchemy import func
from datetime import datetime, timedelta, date
from typing import Dict, List
from app.core.database import get_db
from app.models.session import Session as WorkSession
from app.models.project import Project
from app.models.tag import Tag

router = APIRouter(prefix="/api/statistics", tags=["statistics"])


@router.get("/overview")
def get_overview(
    start_date: date = Query(None),
    end_date: date = Query(None),
    db: Session = Depends(get_db)
) -> Dict:
    """Get overview statistics.

    Returns total sessions, total minutes worked, and average satisfaction score
    for the specified date range.
    """
    if not start_date:
        start_date = date.today() - timedelta(days=30)
    if not end_date:
        end_date = date.today()

    # Total time and sessions
    stats = db.query(
        func.count(WorkSession.id).label('total_sessions'),
        func.sum(WorkSession.actual_duration).label('total_minutes'),
        func.avg(WorkSession.satisfaction_score).label('avg_satisfaction')
    ).filter(
        WorkSession.start_time >= start_date,
        WorkSession.start_time <= end_date + timedelta(days=1),
        WorkSession.end_time.isnot(None)
    ).first()

    return {
        'total_sessions': int(stats.total_sessions or 0),
        'total_minutes': int(stats.total_minutes or 0),
        'avg_satisfaction': float(round(stats.avg_satisfaction or 0, 1))
    }


@router.get("/by-project")
def get_by_project(
    start_date: date = Query(None),
    end_date: date = Query(None),
    db: Session = Depends(get_db)
) -> List[Dict]:
    """Get time spent per project.

    Returns session count and total minutes for each project
    in the specified date range.
    """
    if not start_date:
        start_date = date.today() - timedelta(days=30)
    if not end_date:
        end_date = date.today()

    results = db.query(
        Project.name,
        Project.color,
        func.count(WorkSession.id).label('session_count'),
        func.sum(WorkSession.actual_duration).label('total_minutes')
    ).join(
        WorkSession, WorkSession.project_id == Project.id
    ).filter(
        WorkSession.start_time >= start_date,
        WorkSession.start_time <= end_date + timedelta(days=1),
        WorkSession.end_time.isnot(None)
    ).group_by(
        Project.id
    ).order_by(
        func.sum(WorkSession.actual_duration).desc()
    ).all()

    return [
        {
            'project_name': r.name,
            'color': r.color,
            'session_count': r.session_count,
            'total_minutes': int(r.total_minutes or 0)
        }
        for r in results
    ]


@router.get("/daily-activity")
def get_daily_activity(
    start_date: date = Query(None),
    end_date: date = Query(None),
    db: Session = Depends(get_db)
) -> List[Dict]:
    """Get daily activity summary.

    Returns daily session count, total minutes, and average satisfaction
    for the specified date range.
    """
    if not start_date:
        start_date = date.today() - timedelta(days=30)
    if not end_date:
        end_date = date.today()

    results = db.query(
        func.date(WorkSession.start_time).label('date'),
        func.count(WorkSession.id).label('session_count'),
        func.sum(WorkSession.actual_duration).label('total_minutes'),
        func.avg(WorkSession.satisfaction_score).label('avg_satisfaction')
    ).filter(
        WorkSession.start_time >= start_date,
        WorkSession.start_time <= end_date + timedelta(days=1),
        WorkSession.end_time.isnot(None)
    ).group_by(
        func.date(WorkSession.start_time)
    ).order_by(
        func.date(WorkSession.start_time)
    ).all()

    return [
        {
            'date': str(r.date),
            'session_count': r.session_count,
            'total_minutes': int(r.total_minutes or 0),
            'avg_satisfaction': round(r.avg_satisfaction or 0, 1) if r.avg_satisfaction else 0
        }
        for r in results
    ]


@router.get("/by-tag")
def get_by_tag(
    start_date: date = Query(None),
    end_date: date = Query(None),
    db: Session = Depends(get_db)
) -> List[Dict]:
    """Get time spent per tag.

    Returns session count and total minutes for each tag
    in the specified date range.
    """
    if not start_date:
        start_date = date.today() - timedelta(days=30)
    if not end_date:
        end_date = date.today()

    # This requires joining through the session_tags association table
    from app.models.session import SessionTag

    results = db.query(
        Tag.name,
        Tag.color,
        func.count(WorkSession.id).label('session_count'),
        func.sum(WorkSession.actual_duration).label('total_minutes')
    ).join(
        SessionTag, SessionTag.tag_id == Tag.id
    ).join(
        WorkSession, WorkSession.id == SessionTag.session_id
    ).filter(
        WorkSession.start_time >= start_date,
        WorkSession.start_time <= end_date + timedelta(days=1),
        WorkSession.end_time.isnot(None)
    ).group_by(
        Tag.id
    ).order_by(
        func.sum(WorkSession.actual_duration).desc()
    ).all()

    return [
        {
            'tag_name': r.name,
            'color': r.color,
            'session_count': r.session_count,
            'total_minutes': int(r.total_minutes or 0)
        }
        for r in results
    ]
