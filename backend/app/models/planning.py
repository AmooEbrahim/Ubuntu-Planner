from sqlalchemy import Column, Integer, String, ForeignKey, TIMESTAMP, DateTime, Text, Enum
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.core.database import Base
import enum


class PriorityEnum(str, enum.Enum):
    """Priority levels for planning."""
    low = "low"
    medium = "medium"
    critical = "critical"


class Planning(Base):
    """Planning model for scheduling work."""

    __tablename__ = "planning"

    id = Column(Integer, primary_key=True, index=True)
    project_id = Column(Integer, ForeignKey("projects.id", ondelete="CASCADE"), nullable=False)
    scheduled_start = Column(DateTime, nullable=False, index=True)
    scheduled_end = Column(DateTime, nullable=False, index=True)
    priority = Column(Enum(PriorityEnum), default=PriorityEnum.medium)
    description = Column(Text, nullable=True)
    created_at = Column(TIMESTAMP, server_default=func.now())
    updated_at = Column(TIMESTAMP, server_default=func.now(), onupdate=func.now())

    # Relationships
    project = relationship("Project", back_populates="planning")
    tags = relationship("Tag", secondary="planning_tags")
    sessions = relationship("Session", back_populates="planning")


class PlanningTag(Base):
    """Many-to-many relationship between planning and tags."""

    __tablename__ = "planning_tags"

    planning_id = Column(Integer, ForeignKey("planning.id", ondelete="CASCADE"), primary_key=True)
    tag_id = Column(Integer, ForeignKey("tags.id", ondelete="CASCADE"), primary_key=True)
