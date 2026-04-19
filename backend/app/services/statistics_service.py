"""Statistics service for aggregating work session data."""
from datetime import date, timedelta
from typing import Dict, List
from sqlalchemy import func
from sqlalchemy.orm import Session
from app.models.session import Session as WorkSession, SessionTag
from app.models.project import Project
from app.models.tag import Tag


class StatisticsService:
    """Service for computing statistics from work sessions."""

    def __init__(self, db: Session):
        """Initialize statistics service.

        Args:
            db: Database session
        """
        self.db = db

    def get_default_date_range(self) -> tuple[date, date]:
        """Get default date range (last 30 days).

        Returns:
            Tuple of (start_date, end_date)
        """
        end_date = date.today()
        start_date = end_date - timedelta(days=30)
        return start_date, end_date

    def get_overview(
        self,
        start_date: date | None = None,
        end_date: date | None = None
    ) -> Dict:
        """Get overview statistics.

        Args:
            start_date: Start date for filtering
            end_date: End date for filtering

        Returns:
            Dictionary with total_sessions, total_minutes, avg_satisfaction
        """
        if not start_date or not end_date:
            start_date, end_date = self.get_default_date_range()

        stats = self.db.query(
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

    def get_by_project(
        self,
        start_date: date | None = None,
        end_date: date | None = None
    ) -> List[Dict]:
        """Get time spent per project.

        Args:
            start_date: Start date for filtering
            end_date: End date for filtering

        Returns:
            List of dictionaries with project_name, color, session_count, total_minutes
        """
        if not start_date or not end_date:
            start_date, end_date = self.get_default_date_range()

        results = self.db.query(
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

    def get_daily_activity(
        self,
        start_date: date | None = None,
        end_date: date | None = None
    ) -> List[Dict]:
        """Get daily activity summary.

        Args:
            start_date: Start date for filtering
            end_date: End date for filtering

        Returns:
            List of dictionaries with date, session_count, total_minutes, avg_satisfaction
        """
        if not start_date or not end_date:
            start_date, end_date = self.get_default_date_range()

        results = self.db.query(
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

    def get_by_tag(
        self,
        start_date: date | None = None,
        end_date: date | None = None
    ) -> List[Dict]:
        """Get time spent per tag.

        Args:
            start_date: Start date for filtering
            end_date: End date for filtering

        Returns:
            List of dictionaries with tag_name, color, session_count, total_minutes
        """
        if not start_date or not end_date:
            start_date, end_date = self.get_default_date_range()

        results = self.db.query(
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