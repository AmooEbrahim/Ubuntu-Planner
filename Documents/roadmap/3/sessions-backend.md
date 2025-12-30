# Sessions Backend Implementation

Backend API for session tracking and management.

## Service Layer

Create `backend/app/services/session_service.py`:

```python
from datetime import datetime
from typing import List, Optional
from sqlalchemy.orm import Session as DBSession
from app.models.session import Session
from app.models.tag import Tag

class SessionService:
    def __init__(self, db: DBSession):
        self.db = db

    def get_active_session(self) -> Optional[Session]:
        """Get currently active session."""
        return self.db.query(Session).filter(
            Session.end_time.is_(None)
        ).first()

    def get_by_id(self, session_id: int) -> Optional[Session]:
        """Get session by ID."""
        return self.db.query(Session).filter(Session.id == session_id).first()

    def get_recent(self, limit: int = 20) -> List[Session]:
        """Get recent completed sessions."""
        return self.db.query(Session).filter(
            Session.end_time.isnot(None)
        ).order_by(Session.start_time.desc()).limit(limit).all()

    def start_session(self, session_data: dict) -> Session:
        """Start a new session."""
        # Check if there's already an active session
        active = self.get_active_session()
        if active:
            raise ValueError("Another session is already active")

        # Set start_time if not provided
        if 'start_time' not in session_data:
            session_data['start_time'] = datetime.now()

        # Extract tags
        tag_ids = session_data.pop('tag_ids', [])

        session = Session(**session_data)
        self.db.add(session)

        # Add tags if provided
        if tag_ids:
            tags = self.db.query(Tag).filter(Tag.id.in_(tag_ids)).all()
            session.tags = tags

        self.db.commit()
        self.db.refresh(session)
        return session

    def stop_session(
        self,
        session_id: int,
        review_data: Optional[dict] = None
    ) -> Session:
        """Stop a session, optionally with review data."""
        session = self.get_by_id(session_id)
        if not session:
            raise ValueError("Session not found")

        if session.end_time:
            raise ValueError("Session already stopped")

        # Set end time
        session.end_time = datetime.now()

        # Apply review data if provided
        if review_data:
            for key, value in review_data.items():
                if key == 'tag_ids':
                    tags = self.db.query(Tag).filter(Tag.id.in_(value)).all()
                    session.tags = tags
                else:
                    setattr(session, key, value)

        self.db.commit()
        self.db.refresh(session)
        return session

    def add_note(self, session_id: int, note: str) -> Session:
        """Add note to active session."""
        session = self.get_by_id(session_id)
        if not session:
            raise ValueError("Session not found")

        # Append note with timestamp
        timestamp = datetime.now().strftime("%H:%M")
        new_note = f"[{timestamp}] {note}"

        if session.notes:
            session.notes += f"\n{new_note}"
        else:
            session.notes = new_note

        self.db.commit()
        self.db.refresh(session)
        return session

    def add_time(self, session_id: int, minutes: int) -> Session:
        """Add time to session's planned duration."""
        session = self.get_by_id(session_id)
        if not session:
            raise ValueError("Session not found")

        session.planned_duration += minutes

        self.db.commit()
        self.db.refresh(session)
        return session

    def toggle_notifications(self, session_id: int) -> Session:
        """Toggle notification disabled flag."""
        session = self.get_by_id(session_id)
        if not session:
            raise ValueError("Session not found")

        session.notification_disabled = not session.notification_disabled

        self.db.commit()
        self.db.refresh(session)
        return session
```

## API Routes

Create `backend/app/api/sessions.py`:

```python
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session as DBSession
from typing import List, Optional
from datetime import datetime
from pydantic import BaseModel
from app.core.database import get_db
from app.services.session_service import SessionService

router = APIRouter(prefix="/api/sessions", tags=["sessions"])

class SessionStart(BaseModel):
    project_id: Optional[int] = None
    planned_duration: int
    planning_id: Optional[int] = None
    tag_ids: List[int] = []

class SessionReview(BaseModel):
    satisfaction_score: Optional[int] = None
    tasks_done: Optional[str] = None
    notes: Optional[str] = None
    tag_ids: Optional[List[int]] = None

class SessionResponse(BaseModel):
    id: int
    project_id: Optional[int]
    start_time: datetime
    end_time: Optional[datetime]
    planned_duration: int
    actual_duration: Optional[int]
    notification_disabled: bool
    # Include project, tags, etc.

    class Config:
        from_attributes = True

def get_service(db: DBSession = Depends(get_db)) -> SessionService:
    return SessionService(db)

@router.get("/active", response_model=Optional[SessionResponse])
def get_active_session(service: SessionService = Depends(get_service)):
    """Get currently active session."""
    return service.get_active_session()

@router.get("/recent", response_model=List[SessionResponse])
def get_recent_sessions(
    limit: int = 20,
    service: SessionService = Depends(get_service)
):
    """Get recent sessions."""
    return service.get_recent(limit=limit)

@router.post("/", response_model=SessionResponse, status_code=201)
def start_session(
    data: SessionStart,
    service: SessionService = Depends(get_service)
):
    """Start a new session."""
    try:
        return service.start_session(data.dict())
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.post("/{session_id}/stop", response_model=SessionResponse)
def stop_session(
    session_id: int,
    review: Optional[SessionReview] = None,
    service: SessionService = Depends(get_service)
):
    """Stop a session with optional review."""
    try:
        review_data = review.dict(exclude_unset=True) if review else None
        return service.stop_session(session_id, review_data)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.post("/{session_id}/add-note")
def add_note(
    session_id: int,
    note: str,
    service: SessionService = Depends(get_service)
):
    """Add note to session."""
    try:
        return service.add_note(session_id, note)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.post("/{session_id}/add-time")
def add_time(
    session_id: int,
    minutes: int = 15,
    service: SessionService = Depends(get_service)
):
    """Add time to session."""
    try:
        return service.add_time(session_id, minutes)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.post("/{session_id}/toggle-notifications")
def toggle_notifications(
    session_id: int,
    service: SessionService = Depends(get_service)
):
    """Toggle notifications for session."""
    try:
        return service.toggle_notifications(session_id)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
```

## Checklist

- [ ] SessionService created
- [ ] Single active session enforced
- [ ] API routes created
- [ ] Start session endpoint works
- [ ] Stop session endpoint works
- [ ] Add note works
- [ ] Add time works
- [ ] Toggle notifications works
- [ ] Router included in main.py
