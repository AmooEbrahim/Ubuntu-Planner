"""Day memory service.

Wraps CRUD over the ``day_memories`` table. Each (date, is_ai) pair is unique;
``upsert`` is the natural primary write operation.
"""
from datetime import date as date_type
from typing import List, Optional

from sqlalchemy.orm import Session

from app.models.day_memory import DayMemory


_EDITABLE_FIELDS = (
    "intentions",
    "reflection",
    "lessons",
    "completed",
    "gratitude",
    "free_notes",
    "mood",
)


class DayMemoryService:
    """Service for the day-memory journal."""

    def __init__(self, db: Session) -> None:
        self.db = db

    def get(self, target_date: date_type, is_ai: bool) -> Optional[DayMemory]:
        """Return the memory row for the given date+track, if any."""
        return (
            self.db.query(DayMemory)
            .filter(DayMemory.date == target_date, DayMemory.is_ai == is_ai)
            .first()
        )

    def get_pair(self, target_date: date_type) -> tuple[Optional[DayMemory], Optional[DayMemory]]:
        """Return ``(user_track, ai_track)`` for a given date."""
        rows = (
            self.db.query(DayMemory).filter(DayMemory.date == target_date).all()
        )
        user_row = next((r for r in rows if not r.is_ai), None)
        ai_row = next((r for r in rows if r.is_ai), None)
        return user_row, ai_row

    def list_range(self, start: date_type, end: date_type) -> List[DayMemory]:
        """Return all memory rows in ``[start, end]`` ordered by date asc, user track first."""
        return (
            self.db.query(DayMemory)
            .filter(DayMemory.date >= start, DayMemory.date <= end)
            .order_by(DayMemory.date.asc(), DayMemory.is_ai.asc())
            .all()
        )

    def upsert(self, target_date: date_type, is_ai: bool, data: dict) -> DayMemory:
        """Create or update a day memory record for the given (date, track).

        Only fields present in ``data`` overwrite. Pass an explicit ``None`` to clear.
        """
        row = self.get(target_date, is_ai)
        if row is None:
            row = DayMemory(date=target_date, is_ai=is_ai)
            self.db.add(row)

        for key in _EDITABLE_FIELDS:
            if key in data:
                setattr(row, key, data[key])

        self.db.commit()
        self.db.refresh(row)
        return row

    def delete(self, target_date: date_type, is_ai: bool) -> bool:
        """Delete a day memory row. Returns True if a row was deleted."""
        row = self.get(target_date, is_ai)
        if row is None:
            return False
        self.db.delete(row)
        self.db.commit()
        return True
