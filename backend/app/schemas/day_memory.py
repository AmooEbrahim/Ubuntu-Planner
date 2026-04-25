"""Day memory request/response schemas."""
from datetime import date as date_type, datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict, Field


class DayMemoryUpsert(BaseModel):
    """Payload for upserting a day memory entry.

    Any field omitted is left untouched on update; on create, omitted fields
    default to ``None`` (i.e., empty section).
    """

    intentions: Optional[str] = None
    reflection: Optional[str] = None
    lessons: Optional[str] = None
    completed: Optional[str] = None
    gratitude: Optional[str] = None
    free_notes: Optional[str] = None
    mood: Optional[int] = Field(default=None, ge=1, le=5)


class DayMemoryResponse(BaseModel):
    """A single day-memory record (one track for one date)."""

    id: int
    date: date_type
    is_ai: bool
    intentions: Optional[str]
    reflection: Optional[str]
    lessons: Optional[str]
    completed: Optional[str]
    gratitude: Optional[str]
    free_notes: Optional[str]
    mood: Optional[int]
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class DayMemoryPair(BaseModel):
    """Both tracks for a given date. Either side may be ``None`` if absent."""

    date: date_type
    user: Optional[DayMemoryResponse] = None
    ai: Optional[DayMemoryResponse] = None
