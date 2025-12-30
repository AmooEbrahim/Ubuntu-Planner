"""Session API endpoints for work tracking."""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session as DBSession
from typing import List, Optional
from datetime import datetime
from pydantic import BaseModel
from app.core.database import get_db
from app.services.session_service import SessionService

router = APIRouter(prefix="/api/sessions", tags=["sessions"])


# Pydantic schemas
class TagResponse(BaseModel):
    """Tag response schema."""

    id: int
    name: str
    color: str

    class Config:
        from_attributes = True


class ProjectResponse(BaseModel):
    """Project response schema."""

    id: int
    name: str
    color: str

    class Config:
        from_attributes = True


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
    created_at: datetime
    updated_at: datetime
    project: Optional[ProjectResponse] = None
    tags: List[TagResponse] = []

    class Config:
        from_attributes = True


# Dependency
def get_service(db: DBSession = Depends(get_db)) -> SessionService:
    """Get session service instance.

    Args:
        db: Database session

    Returns:
        SessionService instance
    """
    return SessionService(db)


# Routes
@router.get("/active", response_model=Optional[SessionResponse])
async def get_active_session(service: SessionService = Depends(get_service)):
    """Get currently active session.

    Args:
        service: Session service instance

    Returns:
        Active session or None
    """
    return service.get_active_session()


@router.get("/recent", response_model=List[SessionResponse])
async def get_recent_sessions(
    limit: int = 20, service: SessionService = Depends(get_service)
):
    """Get recent sessions.

    Args:
        limit: Maximum number of sessions to return
        service: Session service instance

    Returns:
        List of recent sessions
    """
    return service.get_recent(limit=limit)


@router.get("/", response_model=List[SessionResponse])
async def list_sessions(service: SessionService = Depends(get_service)):
    """List all sessions.

    Args:
        service: Session service instance

    Returns:
        List of all sessions
    """
    return service.get_all()


@router.get("/{session_id}", response_model=SessionResponse)
async def get_session(session_id: int, service: SessionService = Depends(get_service)):
    """Get a specific session.

    Args:
        session_id: ID of session
        service: Session service instance

    Returns:
        Session

    Raises:
        HTTPException: If session not found
    """
    session = service.get_by_id(session_id)
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
    return session


@router.post("/", response_model=SessionResponse, status_code=201)
async def start_session(data: SessionStart, service: SessionService = Depends(get_service)):
    """Start a new session.

    Args:
        data: Session start data
        service: Session service instance

    Returns:
        Created session

    Raises:
        HTTPException: If validation fails or another session is active
    """
    try:
        return service.start_session(data.model_dump())
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/{session_id}/stop", response_model=SessionResponse)
async def stop_session(
    session_id: int,
    review: Optional[SessionReview] = None,
    service: SessionService = Depends(get_service),
):
    """Stop a session with optional review.

    Args:
        session_id: ID of session to stop
        review: Optional review data
        service: Session service instance

    Returns:
        Updated session

    Raises:
        HTTPException: If session not found or already stopped
    """
    try:
        review_data = review.model_dump(exclude_unset=True) if review else None
        return service.stop_session(session_id, review_data)
    except ValueError as e:
        if "not found" in str(e):
            raise HTTPException(status_code=404, detail=str(e))
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/{session_id}/add-note", response_model=SessionResponse)
async def add_note(
    session_id: int, data: AddNoteRequest, service: SessionService = Depends(get_service)
):
    """Add note to session.

    Args:
        session_id: ID of session
        data: Note data
        service: Session service instance

    Returns:
        Updated session

    Raises:
        HTTPException: If session not found
    """
    try:
        return service.add_note(session_id, data.note)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.post("/{session_id}/add-time", response_model=SessionResponse)
async def add_time(
    session_id: int, data: AddTimeRequest, service: SessionService = Depends(get_service)
):
    """Add time to session.

    Args:
        session_id: ID of session
        data: Time data
        service: Session service instance

    Returns:
        Updated session

    Raises:
        HTTPException: If session not found
    """
    try:
        return service.add_time(session_id, data.minutes)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.post("/{session_id}/toggle-notifications", response_model=SessionResponse)
async def toggle_notifications(session_id: int, service: SessionService = Depends(get_service)):
    """Toggle notifications for session.

    Args:
        session_id: ID of session
        service: Session service instance

    Returns:
        Updated session

    Raises:
        HTTPException: If session not found
    """
    try:
        return service.toggle_notifications(session_id)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
