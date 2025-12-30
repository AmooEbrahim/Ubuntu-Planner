"""Planning service for managing work schedules."""

from datetime import datetime, date
from typing import List, Optional
from sqlalchemy.orm import Session
from app.models.planning import Planning
from app.models.tag import Tag


class PlanningService:
    """Service for managing planning items."""

    def __init__(self, db: Session):
        """Initialize planning service with database session.

        Args:
            db: SQLAlchemy database session
        """
        self.db = db

    def get_by_date(self, target_date: date) -> List[Planning]:
        """Get all planning for a specific date.

        Args:
            target_date: Date to get planning for

        Returns:
            List of planning items for the specified date
        """
        start_of_day = datetime.combine(target_date, datetime.min.time())
        end_of_day = datetime.combine(target_date, datetime.max.time())

        return (
            self.db.query(Planning)
            .filter(
                Planning.scheduled_start >= start_of_day,
                Planning.scheduled_start <= end_of_day,
            )
            .order_by(Planning.scheduled_start)
            .all()
        )

    def get_by_id(self, planning_id: int) -> Optional[Planning]:
        """Get planning by ID.

        Args:
            planning_id: ID of the planning item

        Returns:
            Planning item if found, None otherwise
        """
        return self.db.query(Planning).filter(Planning.id == planning_id).first()

    def get_all(self) -> List[Planning]:
        """Get all planning items.

        Returns:
            List of all planning items
        """
        return (
            self.db.query(Planning)
            .order_by(Planning.scheduled_start.desc())
            .all()
        )

    def check_overlap(
        self, scheduled_start: datetime, scheduled_end: datetime, exclude_id: Optional[int] = None
    ) -> bool:
        """Check if there's an overlap with existing planning.

        Args:
            scheduled_start: Start time of the planning
            scheduled_end: End time of the planning
            exclude_id: ID to exclude from check (for updates)

        Returns:
            True if there's an overlap, False otherwise
        """
        query = self.db.query(Planning).filter(
            Planning.scheduled_start < scheduled_end, Planning.scheduled_end > scheduled_start
        )

        if exclude_id:
            query = query.filter(Planning.id != exclude_id)

        return query.first() is not None

    def validate_same_day(self, scheduled_start: datetime, scheduled_end: datetime) -> bool:
        """Validate that start and end are on the same day.

        Args:
            scheduled_start: Start time
            scheduled_end: End time

        Returns:
            True if same day, False otherwise
        """
        return scheduled_start.date() == scheduled_end.date()

    def create(self, planning_data: dict) -> Planning:
        """Create new planning.

        Args:
            planning_data: Dictionary with planning data

        Returns:
            Created planning item

        Raises:
            ValueError: If validation fails or overlap detected
        """
        # Validation
        if not self.validate_same_day(
            planning_data["scheduled_start"], planning_data["scheduled_end"]
        ):
            raise ValueError("Planning must be within the same day")

        if self.check_overlap(planning_data["scheduled_start"], planning_data["scheduled_end"]):
            raise ValueError("Planning overlaps with existing planning")

        # Validate end time is after start time
        if planning_data["scheduled_end"] <= planning_data["scheduled_start"]:
            raise ValueError("End time must be after start time")

        # Extract tags if provided
        tag_ids = planning_data.pop("tag_ids", [])

        planning = Planning(**planning_data)
        self.db.add(planning)

        # Add tags
        if tag_ids:
            tags = self.db.query(Tag).filter(Tag.id.in_(tag_ids)).all()
            planning.tags = tags

        self.db.commit()
        self.db.refresh(planning)
        return planning

    def update(self, planning_id: int, planning_data: dict) -> Planning:
        """Update planning.

        Args:
            planning_id: ID of planning to update
            planning_data: Dictionary with updated data

        Returns:
            Updated planning item

        Raises:
            ValueError: If planning not found or validation fails
        """
        planning = self.db.query(Planning).filter(Planning.id == planning_id).first()
        if not planning:
            raise ValueError("Planning not found")

        # If changing times, validate
        new_start = planning_data.get("scheduled_start", planning.scheduled_start)
        new_end = planning_data.get("scheduled_end", planning.scheduled_end)

        if not self.validate_same_day(new_start, new_end):
            raise ValueError("Planning must be within the same day")

        # Validate end time is after start time
        if new_end <= new_start:
            raise ValueError("End time must be after start time")

        if self.check_overlap(new_start, new_end, exclude_id=planning_id):
            raise ValueError("Planning overlaps with existing planning")

        # Extract tags if provided
        tag_ids = planning_data.pop("tag_ids", None)

        # Update fields
        for key, value in planning_data.items():
            if hasattr(planning, key):
                setattr(planning, key, value)

        # Update tags if provided
        if tag_ids is not None:
            tags = self.db.query(Tag).filter(Tag.id.in_(tag_ids)).all()
            planning.tags = tags

        self.db.commit()
        self.db.refresh(planning)
        return planning

    def delete(self, planning_id: int) -> bool:
        """Delete planning.

        Args:
            planning_id: ID of planning to delete

        Returns:
            True if deleted, False if not found
        """
        planning = self.db.query(Planning).filter(Planning.id == planning_id).first()
        if not planning:
            return False

        self.db.delete(planning)
        self.db.commit()
        return True
