"""API routes for project management."""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List, Optional
from pydantic import BaseModel, Field
from app.core.database import get_db
from app.models.project import Project
from app.services.project_service import ProjectService

router = APIRouter(prefix="/api/projects", tags=["projects"])


# Pydantic schemas
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

    class Config:
        from_attributes = True


def get_service(db: Session = Depends(get_db)) -> ProjectService:
    """Get project service instance.

    Args:
        db: Database session

    Returns:
        ProjectService instance
    """
    return ProjectService(db)


@router.get("/", response_model=List[ProjectResponse])
async def list_projects(
    include_archived: bool = False,
    service: ProjectService = Depends(get_service)
):
    """List all projects.

    Args:
        include_archived: Whether to include archived projects
        service: Project service instance

    Returns:
        List of projects
    """
    return service.get_all(include_archived=include_archived)


@router.get("/pinned", response_model=List[ProjectResponse])
async def list_pinned_projects(service: ProjectService = Depends(get_service)):
    """List pinned projects.

    Args:
        service: Project service instance

    Returns:
        List of pinned projects
    """
    return [p for p in service.get_all() if p.is_pinned]


@router.get("/{project_id}", response_model=ProjectResponse)
async def get_project(
    project_id: int,
    service: ProjectService = Depends(get_service)
):
    """Get a specific project.

    Args:
        project_id: Project ID
        service: Project service instance

    Returns:
        Project details

    Raises:
        HTTPException: If project not found
    """
    project = service.get_by_id(project_id)
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    return project


@router.post("/", response_model=ProjectResponse, status_code=201)
async def create_project(
    data: ProjectCreate,
    service: ProjectService = Depends(get_service)
):
    """Create a new project.

    Args:
        data: Project creation data
        service: Project service instance

    Returns:
        Created project

    Raises:
        HTTPException: If validation fails
    """
    try:
        return service.create(data.dict())
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.put("/{project_id}", response_model=ProjectResponse)
async def update_project(
    project_id: int,
    data: ProjectUpdate,
    service: ProjectService = Depends(get_service)
):
    """Update a project.

    Args:
        project_id: Project ID
        data: Project update data
        service: Project service instance

    Returns:
        Updated project

    Raises:
        HTTPException: If validation fails or project not found
    """
    try:
        return service.update(project_id, data.dict(exclude_unset=True))
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.delete("/{project_id}", status_code=204)
async def delete_project(
    project_id: int,
    service: ProjectService = Depends(get_service)
):
    """Delete a project.

    Args:
        project_id: Project ID
        service: Project service instance

    Raises:
        HTTPException: If project not found
    """
    if not service.delete(project_id):
        raise HTTPException(status_code=404, detail="Project not found")
