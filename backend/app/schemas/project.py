"""Project schemas for request/response validation."""
from typing import Optional
from pydantic import BaseModel, ConfigDict, Field


class ProjectCreate(BaseModel):
    """Schema for creating a project."""

    name: str = Field(..., min_length=1, max_length=255)
    parent_id: Optional[int] = None
    color: str = Field(..., pattern=r'^#[0-9A-Fa-f]{6}$')
    description: Optional[str] = None
    default_duration: int = Field(default=60, ge=5)
    notification_interval: Optional[int] = Field(None, ge=1)
    is_pinned: bool = False


class ProjectUpdate(BaseModel):
    """Schema for updating a project."""

    name: Optional[str] = Field(None, min_length=1, max_length=255)
    parent_id: Optional[int] = None
    color: Optional[str] = Field(None, pattern=r'^#[0-9A-Fa-f]{6}$')
    description: Optional[str] = None
    default_duration: Optional[int] = Field(None, ge=5)
    notification_interval: Optional[int] = Field(None, ge=1)
    is_archived: Optional[bool] = None
    is_pinned: Optional[bool] = None


class ProjectResponse(BaseModel):
    """Schema for project response."""

    id: int
    name: str
    parent_id: Optional[int]
    color: str
    description: Optional[str]
    default_duration: int
    notification_interval: Optional[int]
    is_archived: bool
    is_pinned: bool

    model_config = ConfigDict(from_attributes=True)