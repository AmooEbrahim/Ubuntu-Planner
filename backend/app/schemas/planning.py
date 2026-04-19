"""Planning schemas for request/response validation."""
from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel, ConfigDict, Field

from app.schemas.tag import TagResponse


class ProjectResponse(BaseModel):
    """Project response schema."""

    id: int
    name: str
    color: str

    model_config = ConfigDict(from_attributes=True)


class PlanningCreate(BaseModel):
    """Schema for creating planning."""

    project_id: int
    scheduled_start: datetime
    scheduled_end: datetime
    priority: str = Field(default="medium", pattern="^(low|medium|critical)$")
    description: Optional[str] = None
    tag_ids: List[int] = []


class PlanningUpdate(BaseModel):
    """Schema for updating planning."""

    project_id: Optional[int] = None
    scheduled_start: Optional[datetime] = None
    scheduled_end: Optional[datetime] = None
    priority: Optional[str] = Field(default=None, pattern="^(low|medium|critical)$")
    description: Optional[str] = None
    tag_ids: Optional[List[int]] = None


class PlanningResponse(BaseModel):
    """Schema for planning response."""

    id: int
    project_id: int
    scheduled_start: datetime
    scheduled_end: datetime
    priority: str
    description: Optional[str]
    created_at: datetime
    updated_at: datetime
    project: ProjectResponse
    tags: List[TagResponse] = []

    model_config = ConfigDict(from_attributes=True)