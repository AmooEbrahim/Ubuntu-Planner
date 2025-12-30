"""Project service for business logic."""
from typing import List, Optional
from sqlalchemy.orm import Session
from app.models.project import Project


class ProjectService:
    """Service for managing projects."""

    def __init__(self, db: Session):
        """Initialize project service.

        Args:
            db: Database session
        """
        self.db = db

    def get_all(self, include_archived: bool = False) -> List[Project]:
        """Get all projects.

        Args:
            include_archived: Whether to include archived projects

        Returns:
            List of projects
        """
        query = self.db.query(Project)
        if not include_archived:
            query = query.filter(Project.is_archived == False)
        return query.all()

    def get_by_id(self, project_id: int) -> Optional[Project]:
        """Get project by ID.

        Args:
            project_id: Project ID

        Returns:
            Project if found, None otherwise
        """
        return self.db.query(Project).filter(Project.id == project_id).first()

    def create(self, project_data: dict) -> Project:
        """Create new project.

        Args:
            project_data: Project data dictionary

        Returns:
            Created project

        Raises:
            ValueError: If parent project not found or circular reference detected
        """
        # Validate parent exists (if provided)
        if project_data.get('parent_id'):
            parent = self.get_by_id(project_data['parent_id'])
            if not parent:
                raise ValueError("Parent project not found")

            # Check for circular reference
            if self._would_create_cycle(project_data['parent_id'], None):
                raise ValueError("Circular reference detected")

        project = Project(**project_data)
        self.db.add(project)
        self.db.commit()
        self.db.refresh(project)
        return project

    def update(self, project_id: int, project_data: dict) -> Project:
        """Update project.

        Args:
            project_id: Project ID
            project_data: Updated project data

        Returns:
            Updated project

        Raises:
            ValueError: If project not found or circular reference detected
        """
        project = self.get_by_id(project_id)
        if not project:
            raise ValueError("Project not found")

        # If changing parent, validate
        if 'parent_id' in project_data:
            if project_data['parent_id']:
                parent = self.get_by_id(project_data['parent_id'])
                if not parent:
                    raise ValueError("Parent project not found")

                if self._would_create_cycle(project_data['parent_id'], project_id):
                    raise ValueError("Circular reference detected")

        for key, value in project_data.items():
            setattr(project, key, value)

        self.db.commit()
        self.db.refresh(project)
        return project

    def delete(self, project_id: int) -> bool:
        """Delete project.

        Args:
            project_id: Project ID

        Returns:
            True if deleted, False if not found
        """
        project = self.get_by_id(project_id)
        if not project:
            return False

        # CASCADE will handle child projects, planning, and sessions
        self.db.delete(project)
        self.db.commit()
        return True

    def _would_create_cycle(self, parent_id: int, project_id: Optional[int]) -> bool:
        """Check if setting parent would create a cycle.

        Args:
            parent_id: Proposed parent ID
            project_id: Current project ID (None for new projects)

        Returns:
            True if cycle would be created, False otherwise
        """
        current = parent_id
        visited = set()

        while current:
            if current == project_id:
                return True
            if current in visited:
                break
            visited.add(current)

            parent = self.get_by_id(current)
            current = parent.parent_id if parent else None

        return False
