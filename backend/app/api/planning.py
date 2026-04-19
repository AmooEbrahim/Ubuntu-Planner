"""Planning API endpoints for scheduling work."""

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import date
from app.core.database import get_db
from app.services.planning_service import PlanningService
from app.schemas.planning import PlanningCreate, PlanningUpdate, PlanningResponse


router = APIRouter(prefix="/api/planning", tags=["planning"])


def get_service(db: Session = Depends(get_db)) -> PlanningService:
    """Get planning service instance.

    Args:
        db: Database session

    Returns:
        PlanningService instance
    """
    return PlanningService(db)


@router.get("/", response_model=List[PlanningResponse])
async def list_planning(
    date_filter: Optional[date] = Query(None, alias="date"),
    service: PlanningService = Depends(get_service),
):
    """List planning items, optionally filtered by date.

    Args:
        date_filter: Optional date to filter planning
        service: Planning service instance

    Returns:
        List of planning items
    """
    if date_filter:
        return service.get_by_date(date_filter)
    return service.get_all()


@router.get("/today", response_model=List[PlanningResponse])
async def today_planning(service: PlanningService = Depends(get_service)):
    """Get today's planning.

    Args:
        service: Planning service instance

    Returns:
        List of today's planning items
    """
    return service.get_by_date(date.today())


@router.get("/{planning_id}", response_model=PlanningResponse)
async def get_planning(planning_id: int, service: PlanningService = Depends(get_service)):
    """Get a specific planning item.

    Args:
        planning_id: ID of planning item
        service: Planning service instance

    Returns:
        Planning item

    Raises:
        HTTPException: If planning not found
    """
    planning = service.get_by_id(planning_id)
    if not planning:
        raise HTTPException(status_code=404, detail="Planning not found")
    return planning


@router.post("/", response_model=PlanningResponse, status_code=201)
async def create_planning(data: PlanningCreate, service: PlanningService = Depends(get_service)):
    """Create a new planning item.

    Args:
        data: Planning creation data
        service: Planning service instance

    Returns:
        Created planning item

    Raises:
        HTTPException: If validation fails
    """
    try:
        return service.create(data.model_dump())
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.put("/{planning_id}", response_model=PlanningResponse)
async def update_planning(
    planning_id: int, data: PlanningUpdate, service: PlanningService = Depends(get_service)
):
    """Update a planning item.

    Args:
        planning_id: ID of planning to update
        data: Planning update data
        service: Planning service instance

    Returns:
        Updated planning item

    Raises:
        HTTPException: If planning not found or validation fails
    """
    try:
        return service.update(planning_id, data.model_dump(exclude_unset=True))
    except ValueError as e:
        if "not found" in str(e):
            raise HTTPException(status_code=404, detail=str(e))
        raise HTTPException(status_code=400, detail=str(e))


@router.delete("/{planning_id}", status_code=204)
async def delete_planning(planning_id: int, service: PlanningService = Depends(get_service)):
    """Delete a planning item.

    Args:
        planning_id: ID of planning to delete
        service: Planning service instance

    Raises:
        HTTPException: If planning not found
    """
    if not service.delete(planning_id):
        raise HTTPException(status_code=404, detail="Planning not found")