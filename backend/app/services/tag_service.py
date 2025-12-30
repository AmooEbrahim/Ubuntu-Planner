"""Tag service for business logic."""
from typing import List, Optional
from sqlalchemy.orm import Session
from app.models.tag import Tag
from app.models.project import Project


class TagService:
    """Service for managing tags."""

    def __init__(self, db: Session):
        """Initialize tag service.

        Args:
            db: Database session
        """
        self.db = db

    def get_all(self) -> List[Tag]:
        """Get all tags.

        Returns:
            List of all tags
        """
        return self.db.query(Tag).all()

    def get_by_id(self, tag_id: int) -> Optional[Tag]:
        """Get tag by ID.

        Args:
            tag_id: Tag ID

        Returns:
            Tag if found, None otherwise
        """
        return self.db.query(Tag).filter(Tag.id == tag_id).first()

    def get_available_for_project(self, project_id: int) -> List[Tag]:
        """Get tags available for a project (global + project + parent projects).

        This implements tag inheritance: a project can use global tags,
        its own tags, and tags from all ancestor projects.

        Args:
            project_id: Project ID

        Returns:
            List of available tags for the project
        """
        project = self.db.query(Project).filter(Project.id == project_id).first()
        if not project:
            return []

        # Start with global tags
        tags = list(self.db.query(Tag).filter(Tag.project_id.is_(None)).all())
        tag_ids = {tag.id for tag in tags}

        # Add project and ancestor tags
        current_project = project
        while current_project:
            project_tags = self.db.query(Tag).filter(
                Tag.project_id == current_project.id
            ).all()

            # Add only unique tags
            for tag in project_tags:
                if tag.id not in tag_ids:
                    tags.append(tag)
                    tag_ids.add(tag.id)

            # Move to parent project
            current_project = self.db.query(Project).filter(
                Project.id == current_project.parent_id
            ).first() if current_project.parent_id else None

        return tags

    def create(self, tag_data: dict) -> Tag:
        """Create new tag.

        Args:
            tag_data: Tag data dictionary

        Returns:
            Created tag

        Raises:
            ValueError: If tag with this name already exists in the scope
        """
        # Check uniqueness in scope (global or specific project)
        existing = self.db.query(Tag).filter(
            Tag.name == tag_data['name'],
            Tag.project_id == tag_data.get('project_id')
        ).first()

        if existing:
            scope = "globally" if not tag_data.get('project_id') else "in this project"
            raise ValueError(f"Tag with name '{tag_data['name']}' already exists {scope}")

        # Validate project exists if project_id provided
        if tag_data.get('project_id'):
            project = self.db.query(Project).filter(
                Project.id == tag_data['project_id']
            ).first()
            if not project:
                raise ValueError("Project not found")

        tag = Tag(**tag_data)
        self.db.add(tag)
        self.db.commit()
        self.db.refresh(tag)
        return tag

    def update(self, tag_id: int, tag_data: dict) -> Tag:
        """Update tag.

        Args:
            tag_id: Tag ID
            tag_data: Updated tag data

        Returns:
            Updated tag

        Raises:
            ValueError: If tag not found or name conflict
        """
        tag = self.get_by_id(tag_id)
        if not tag:
            raise ValueError("Tag not found")

        # If changing name or project_id, check uniqueness
        if 'name' in tag_data or 'project_id' in tag_data:
            new_name = tag_data.get('name', tag.name)
            new_project_id = tag_data.get('project_id', tag.project_id)

            existing = self.db.query(Tag).filter(
                Tag.name == new_name,
                Tag.project_id == new_project_id,
                Tag.id != tag_id
            ).first()

            if existing:
                scope = "globally" if not new_project_id else "in this project"
                raise ValueError(f"Tag with name '{new_name}' already exists {scope}")

        # Validate project exists if project_id provided
        if 'project_id' in tag_data and tag_data['project_id']:
            project = self.db.query(Project).filter(
                Project.id == tag_data['project_id']
            ).first()
            if not project:
                raise ValueError("Project not found")

        for key, value in tag_data.items():
            setattr(tag, key, value)

        self.db.commit()
        self.db.refresh(tag)
        return tag

    def delete(self, tag_id: int) -> bool:
        """Delete tag.

        Args:
            tag_id: Tag ID

        Returns:
            True if deleted, False if not found
        """
        tag = self.get_by_id(tag_id)
        if not tag:
            return False

        self.db.delete(tag)
        self.db.commit()
        return True
