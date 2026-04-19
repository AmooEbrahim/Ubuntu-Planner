"""API routes for tag management."""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from app.core.database import get_db
from app.services.tag_service import TagService
from app.schemas.tag import TagCreate, TagUpdate, TagResponse


router = APIRouter(prefix="/api/tags", tags=["tags"])


def get_service(db: Session = Depends(get_db)) -> TagService:
    """Get tag service instance.

    Args:
        db: Database session

    Returns:
        TagService instance
    """
    return TagService(db)


@router.get("/", response_model=List[TagResponse])
async def list_tags(service: TagService = Depends(get_service)):
    """List all tags.

    Args:
        service: Tag service instance

    Returns:
        List of all tags
    """
    return service.get_all()


@router.get("/project/{project_id}", response_model=List[TagResponse])
async def list_tags_for_project(
    project_id: int,
    service: TagService = Depends(get_service)
):
    """List tags available for a specific project (includes inherited tags).

    Args:
        project_id: Project ID
        service: Tag service instance

    Returns:
        List of tags available for the project
    """
    return service.get_available_for_project(project_id)


@router.get("/{tag_id}", response_model=TagResponse)
async def get_tag(
    tag_id: int,
    service: TagService = Depends(get_service)
):
    """Get a specific tag.

    Args:
        tag_id: Tag ID
        service: Tag service instance

    Returns:
        Tag details

    Raises:
        HTTPException: If tag not found
    """
    tag = service.get_by_id(tag_id)
    if not tag:
        raise HTTPException(status_code=404, detail="Tag not found")
    return tag


@router.post("/", response_model=TagResponse, status_code=201)
async def create_tag(
    data: TagCreate,
    service: TagService = Depends(get_service)
):
    """Create a new tag.

    Args:
        data: Tag creation data
        service: Tag service instance

    Returns:
        Created tag

    Raises:
        HTTPException: If validation fails
    """
    try:
        return service.create(data.model_dump())
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.put("/{tag_id}", response_model=TagResponse)
async def update_tag(
    tag_id: int,
    data: TagUpdate,
    service: TagService = Depends(get_service)
):
    """Update a tag.

    Args:
        tag_id: Tag ID
        data: Tag update data
        service: Tag service instance

    Returns:
        Updated tag

    Raises:
        HTTPException: If validation fails or tag not found
    """
    try:
        return service.update(tag_id, data.model_dump(exclude_unset=True))
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.delete("/{tag_id}", status_code=204)
async def delete_tag(
    tag_id: int,
    service: TagService = Depends(get_service)
):
    """Delete a tag.

    Args:
        tag_id: Tag ID
        service: Tag service instance

    Raises:
        HTTPException: If tag not found
    """
    if not service.delete(tag_id):
        raise HTTPException(status_code=404, detail="Tag not found")