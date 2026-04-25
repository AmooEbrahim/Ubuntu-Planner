"""Session schemas for request/response validation."""
from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel, ConfigDict

from app.schemas.tag import TagResponse


class ProjectResponse(BaseModel):
    """Project response schema."""

    id: int
    name: str
    color: str

    model_config = ConfigDict(from_attributes=True)


class SessionStart(BaseModel):
    """Schema for starting a session."""

    project_id: Optional[int] = None
    planned_duration: int
    planning_id: Optional[int] = None
    tag_ids: List[int] = []


class SessionReview(BaseModel):
    """Schema for session review data."""

    satisfaction_score: Optional[int] = None
    tasks_done: Optional[str] = None
    notes: Optional[str] = None
    tag_ids: Optional[List[int]] = None


class SessionReviewUpdate(BaseModel):
    """Schema for updating session review (from review page)."""

    satisfaction: int
    tasks: Optional[str] = None
    notes: Optional[str] = None


class SessionUpdate(BaseModel):
    """Schema for updating a session."""

    project_id: Optional[int] = None
    planned_duration: Optional[int] = None
    actual_duration: Optional[int] = None
    satisfaction_score: Optional[int] = None
    tasks_done: Optional[str] = None
    notes: Optional[str] = None
    tag_ids: Optional[List[int]] = None
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None


class AddNoteRequest(BaseModel):
    """Schema for adding a note."""

    note: str


class AddTimeRequest(BaseModel):
    """Schema for adding time."""

    minutes: int = 15


class SessionResponse(BaseModel):
    """Schema for session response."""

    id: int
    project_id: Optional[int]
    start_time: datetime
    end_time: Optional[datetime]
    planned_duration: int
    actual_duration: Optional[int]
    planning_id: Optional[int]
    notes: Optional[str]
    satisfaction_score: Optional[int]
    tasks_done: Optional[str]
    notification_disabled: bool
    elapsed_minutes: Optional[int] = None
    created_at: datetime
    updated_at: datetime
    project: Optional[ProjectResponse] = None
    tags: List[TagResponse] = []

    model_config = ConfigDict(from_attributes=True)