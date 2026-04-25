"""Day memory model for daily journaling.

Each calendar date can have up to two parallel records:
- ``is_ai = False`` — the user's own journal entry.
- ``is_ai = True``  — the AI's separate observations / reflections.

The two tracks coexist; the AI may only edit the user track when the
appropriate permission is granted.
"""
from sqlalchemy import (
    Boolean,
    CheckConstraint,
    Column,
    Date,
    Integer,
    SmallInteger,
    Text,
    TIMESTAMP,
    UniqueConstraint,
)
from sqlalchemy.sql import func

from app.core.database import Base


class DayMemory(Base):
    """A single day's journal entry for either the user or the AI track."""

    __tablename__ = "day_memories"
    __table_args__ = (
        UniqueConstraint("date", "is_ai", name="uq_day_memories_date_is_ai"),
        CheckConstraint("mood IS NULL OR (mood >= 1 AND mood <= 5)", name="ck_day_memories_mood_range"),
    )

    id = Column(Integer, primary_key=True, index=True)
    date = Column(Date, nullable=False, index=True)
    is_ai = Column(Boolean, nullable=False, default=False, server_default="0")

    intentions = Column(Text, nullable=True)
    reflection = Column(Text, nullable=True)
    lessons = Column(Text, nullable=True)
    completed = Column(Text, nullable=True)
    gratitude = Column(Text, nullable=True)
    free_notes = Column(Text, nullable=True)
    mood = Column(SmallInteger, nullable=True)

    created_at = Column(TIMESTAMP, server_default=func.now())
    updated_at = Column(TIMESTAMP, server_default=func.now(), onupdate=func.now())
