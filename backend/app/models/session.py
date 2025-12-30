from sqlalchemy import Column, Integer, ForeignKey, TIMESTAMP, DateTime, Text, Boolean, Computed
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.core.database import Base


class Session(Base):
    """Session model for tracking actual work time."""

    __tablename__ = "sessions"

    id = Column(Integer, primary_key=True, index=True)
    project_id = Column(Integer, ForeignKey("projects.id", ondelete="SET NULL"), nullable=True)
    start_time = Column(DateTime, nullable=False)
    end_time = Column(DateTime, nullable=True, index=True)
    planned_duration = Column(Integer, nullable=False)
    actual_duration = Column(
        Integer,
        Computed(
            "CASE WHEN end_time IS NULL THEN NULL "
            "ELSE TIMESTAMPDIFF(MINUTE, start_time, end_time) END",
            persisted=True
        )
    )
    planning_id = Column(Integer, ForeignKey("planning.id", ondelete="SET NULL"), nullable=True)
    notes = Column(Text, nullable=True)
    satisfaction_score = Column(Integer, nullable=True)
    tasks_done = Column(Text, nullable=True)
    notification_disabled = Column(Boolean, default=False)
    created_at = Column(TIMESTAMP, server_default=func.now())
    updated_at = Column(TIMESTAMP, server_default=func.now(), onupdate=func.now())

    # Relationships
    project = relationship("Project", back_populates="sessions")
    planning = relationship("Planning", back_populates="sessions")
    tags = relationship("Tag", secondary="session_tags")


class SessionTag(Base):
    """Many-to-many relationship between sessions and tags."""

    __tablename__ = "session_tags"

    session_id = Column(Integer, ForeignKey("sessions.id", ondelete="CASCADE"), primary_key=True)
    tag_id = Column(Integer, ForeignKey("tags.id", ondelete="CASCADE"), primary_key=True)
