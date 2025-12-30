"""Session service for managing work tracking sessions."""

from datetime import datetime
from typing import List, Optional
from sqlalchemy.orm import Session as DBSession
from app.models.session import Session
from app.models.tag import Tag


class SessionService:
    """Service for managing work sessions."""

    def __init__(self, db: DBSession):
        """Initialize session service with database session.

        Args:
            db: SQLAlchemy database session
        """
        self.db = db

    def get_active_session(self) -> Optional[Session]:
        """Get currently active session.

        Returns:
            Active session if exists, None otherwise
        """
        return self.db.query(Session).filter(Session.end_time.is_(None)).first()

    def get_by_id(self, session_id: int) -> Optional[Session]:
        """Get session by ID.

        Args:
            session_id: ID of the session

        Returns:
            Session if found, None otherwise
        """
        return self.db.query(Session).filter(Session.id == session_id).first()

    def get_recent(self, limit: int = 20) -> List[Session]:
        """Get recent completed sessions.

        Args:
            limit: Maximum number of sessions to return

        Returns:
            List of recent completed sessions
        """
        return (
            self.db.query(Session)
            .filter(Session.end_time.isnot(None))
            .order_by(Session.start_time.desc())
            .limit(limit)
            .all()
        )

    def get_all(self) -> List[Session]:
        """Get all sessions.

        Returns:
            List of all sessions
        """
        return self.db.query(Session).order_by(Session.start_time.desc()).all()

    def start_session(self, session_data: dict) -> Session:
        """Start a new session.

        Args:
            session_data: Dictionary with session data

        Returns:
            Created session

        Raises:
            ValueError: If another session is already active
        """
        # Check if there's already an active session
        active = self.get_active_session()
        if active:
            raise ValueError("Another session is already active")

        # Set start_time if not provided
        if "start_time" not in session_data:
            session_data["start_time"] = datetime.now()

        # Extract tags
        tag_ids = session_data.pop("tag_ids", [])

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
        self, session_id: int, review_data: Optional[dict] = None
    ) -> Session:
        """Stop a session, optionally with review data.

        Args:
            session_id: ID of session to stop
            review_data: Optional review data dictionary

        Returns:
            Updated session

        Raises:
            ValueError: If session not found or already stopped
        """
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
                if key == "tag_ids":
                    tags = self.db.query(Tag).filter(Tag.id.in_(value)).all()
                    session.tags = tags
                elif hasattr(session, key):
                    setattr(session, key, value)

        self.db.commit()
        self.db.refresh(session)
        return session

    def add_note(self, session_id: int, note: str) -> Session:
        """Add note to active session.

        Args:
            session_id: ID of session
            note: Note text to add

        Returns:
            Updated session

        Raises:
            ValueError: If session not found
        """
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
        """Add time to session's planned duration.

        Args:
            session_id: ID of session
            minutes: Minutes to add

        Returns:
            Updated session

        Raises:
            ValueError: If session not found
        """
        session = self.get_by_id(session_id)
        if not session:
            raise ValueError("Session not found")

        session.planned_duration += minutes

        self.db.commit()
        self.db.refresh(session)
        return session

    def toggle_notifications(self, session_id: int) -> Session:
        """Toggle notification disabled flag.

        Args:
            session_id: ID of session

        Returns:
            Updated session

        Raises:
            ValueError: If session not found
        """
        session = self.get_by_id(session_id)
        if not session:
            raise ValueError("Session not found")

        session.notification_disabled = not session.notification_disabled

        self.db.commit()
        self.db.refresh(session)
        return session
