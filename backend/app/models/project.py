from sqlalchemy import Column, Integer, String, Boolean, Text, ForeignKey, TIMESTAMP
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.core.database import Base


class Project(Base):
    """Project model for organizing work."""

    __tablename__ = "projects"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False)
    parent_id = Column(Integer, ForeignKey("projects.id"), nullable=True)
    color = Column(String(7), nullable=False)
    description = Column(Text, nullable=True)
    default_duration = Column(Integer, nullable=False, default=60)
    notification_interval = Column(Integer, nullable=True)
    is_archived = Column(Boolean, default=False, index=True)
    is_pinned = Column(Boolean, default=False, index=True)
    created_at = Column(TIMESTAMP, server_default=func.now())
    updated_at = Column(TIMESTAMP, server_default=func.now(), onupdate=func.now())

    # Relationships
    parent = relationship("Project", remote_side=[id], back_populates="children")
    children = relationship("Project", back_populates="parent")
    tags = relationship("Tag", back_populates="project")
    planning = relationship("Planning", back_populates="project")
    sessions = relationship("Session", back_populates="project")
