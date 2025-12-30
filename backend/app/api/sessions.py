from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.core.database import get_db

router = APIRouter(prefix="/api/sessions", tags=["sessions"])


@router.get("/")
async def list_sessions(db: Session = Depends(get_db)):
    """List all sessions."""
    return {"message": "Sessions endpoint - to be implemented"}


@router.post("/")
async def create_session(db: Session = Depends(get_db)):
    """Create/start a new session."""
    return {"message": "Create session - to be implemented"}


@router.get("/active")
async def get_active_session(db: Session = Depends(get_db)):
    """Get the currently active session."""
    return {"message": "Get active session - to be implemented"}


@router.get("/{session_id}")
async def get_session(session_id: int, db: Session = Depends(get_db)):
    """Get a specific session."""
    return {"message": f"Get session {session_id} - to be implemented"}


@router.put("/{session_id}")
async def update_session(session_id: int, db: Session = Depends(get_db)):
    """Update a session."""
    return {"message": f"Update session {session_id} - to be implemented"}


@router.post("/{session_id}/end")
async def end_session(session_id: int, db: Session = Depends(get_db)):
    """End an active session."""
    return {"message": f"End session {session_id} - to be implemented"}
