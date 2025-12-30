# Tags Backend Implementation

Backend API and business logic for tag management.

## Model

Create `backend/app/models/tag.py` (if not created in Phase 0):

Already covered in database schema. Verify it includes:
- name, color, project_id (nullable for global)
- Unique constraint on (name, project_id)
- Relationship to Project

## Service Layer

Create `backend/app/services/tag_service.py`:

```python
from typing import List, Optional
from sqlalchemy.orm import Session
from app.models.tag import Tag
from app.models.project import Project

class TagService:
    def __init__(self, db: Session):
        self.db = db

    def get_all(self) -> List[Tag]:
        """Get all tags."""
        return self.db.query(Tag).all()

    def get_available_for_project(self, project_id: int) -> List[Tag]:
        """Get tags available for a project (global + project + parents)."""
        project = self.db.query(Project).filter(Project.id == project_id).first()
        if not project:
            return []

        # Global tags
        tags = self.db.query(Tag).filter(Tag.project_id.is_(None)).all()

        # Project and ancestor tags
        current_project = project
        while current_project:
            project_tags = self.db.query(Tag).filter(
                Tag.project_id == current_project.id
            ).all()
            tags.extend(project_tags)

            current_project = self.db.query(Project).filter(
                Project.id == current_project.parent_id
            ).first() if current_project.parent_id else None

        return tags

    def create(self, tag_data: dict) -> Tag:
        """Create new tag."""
        # Check uniqueness in scope
        existing = self.db.query(Tag).filter(
            Tag.name == tag_data['name'],
            Tag.project_id == tag_data.get('project_id')
        ).first()

        if existing:
            raise ValueError("Tag with this name already exists in this scope")

        tag = Tag(**tag_data)
        self.db.add(tag)
        self.db.commit()
        self.db.refresh(tag)
        return tag

    def update(self, tag_id: int, tag_data: dict) -> Tag:
        """Update tag."""
        tag = self.db.query(Tag).filter(Tag.id == tag_id).first()
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
                raise ValueError("Tag with this name already exists in this scope")

        for key, value in tag_data.items():
            setattr(tag, key, value)

        self.db.commit()
        self.db.refresh(tag)
        return tag

    def delete(self, tag_id: int) -> bool:
        """Delete tag."""
        tag = self.db.query(Tag).filter(Tag.id == tag_id).first()
        if not tag:
            return False

        self.db.delete(tag)
        self.db.commit()
        return True
```

## API Routes

Create `backend/app/api/tags.py`:

```python
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List, Optional
from pydantic import BaseModel
from app.core.database import get_db
from app.services.tag_service import TagService

router = APIRouter(prefix="/api/tags", tags=["tags"])

class TagCreate(BaseModel):
    name: str
    color: str
    project_id: Optional[int] = None

class TagUpdate(BaseModel):
    name: Optional[str] = None
    color: Optional[str] = None
    project_id: Optional[int] = None

class TagResponse(BaseModel):
    id: int
    name: str
    color: str
    project_id: Optional[int]

    class Config:
        from_attributes = True

def get_service(db: Session = Depends(get_db)) -> TagService:
    return TagService(db)

@router.get("/", response_model=List[TagResponse])
def list_tags(service: TagService = Depends(get_service)):
    return service.get_all()

@router.get("/project/{project_id}", response_model=List[TagResponse])
def list_tags_for_project(
    project_id: int,
    service: TagService = Depends(get_service)
):
    return service.get_available_for_project(project_id)

@router.post("/", response_model=TagResponse, status_code=201)
def create_tag(
    data: TagCreate,
    service: TagService = Depends(get_service)
):
    try:
        return service.create(data.dict())
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.put("/{tag_id}", response_model=TagResponse)
def update_tag(
    tag_id: int,
    data: TagUpdate,
    service: TagService = Depends(get_service)
):
    try:
        return service.update(tag_id, data.dict(exclude_unset=True))
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.delete("/{tag_id}", status_code=204)
def delete_tag(
    tag_id: int,
    service: TagService = Depends(get_service)
):
    if not service.delete(tag_id):
        raise HTTPException(status_code=404, detail="Tag not found")
```

## Checklist

- [ ] TagService created
- [ ] Tag inheritance logic implemented
- [ ] Uniqueness validation works
- [ ] API routes created
- [ ] Router included in main.py
- [ ] Tested with curl/Postman
