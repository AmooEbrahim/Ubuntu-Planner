"""Tag schemas for request/response validation."""
from typing import Optional
from pydantic import BaseModel, ConfigDict, Field


class TagCreate(BaseModel):
    """Schema for creating a tag."""

    name: str = Field(..., min_length=1, max_length=100)
    color: str = Field(..., pattern=r'^#[0-9A-Fa-f]{6}$')
    project_id: Optional[int] = None


class TagUpdate(BaseModel):
    """Schema for updating a tag."""

    name: Optional[str] = Field(None, min_length=1, max_length=100)
    color: Optional[str] = Field(None, pattern=r'^#[0-9A-Fa-f]{6}$')
    project_id: Optional[int] = None


class TagResponse(BaseModel):
    """Schema for tag response."""

    id: int
    name: str
    color: str
    project_id: Optional[int]

    model_config = ConfigDict(from_attributes=True)