# Projects Backend Implementation

Backend API and business logic for project management.

## Model

Already created in Phase 0: `backend/app/models/project.py`

**Verify it includes:**
- All fields from schema (name, parent_id, color, description, default_duration, notification_interval, is_archived, is_pinned)
- Timestamps (created_at, updated_at)
- Self-referential relationship for parent/children

## Service Layer

Create `backend/app/services/project_service.py`:

```python
from typing import List, Optional
from sqlalchemy.orm import Session
from app.models.project import Project

class ProjectService:
    def __init__(self, db: Session):
        self.db = db

    def get_all(self, include_archived: bool = False) -> List[Project]:
        """Get all projects."""
        query = self.db.query(Project)
        if not include_archived:
            query = query.filter(Project.is_archived == False)
        return query.all()

    def get_by_id(self, project_id: int) -> Optional[Project]:
        """Get project by ID."""
        return self.db.query(Project).filter(Project.id == project_id).first()

    def create(self, project_data: dict) -> Project:
        """Create new project."""
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
        """Update project."""
        project = self.get_by_id(project_id)
        if not project:
            raise ValueError("Project not found")

        # If changing parent, validate
        if 'parent_id' in project_data:
            if project_data['parent_id']:
                if self._would_create_cycle(project_data['parent_id'], project_id):
                    raise ValueError("Circular reference detected")

        for key, value in project_data.items():
            setattr(project, key, value)

        self.db.commit()
        self.db.refresh(project)
        return project

    def delete(self, project_id: int) -> bool:
        """Delete project."""
        project = self.get_by_id(project_id)
        if not project:
            return False

        # Check for dependencies (planning, sessions)
        # For now, just delete (CASCADE will handle)
        self.db.delete(project)
        self.db.commit()
        return True

    def _would_create_cycle(self, parent_id: int, project_id: Optional[int]) -> bool:
        """Check if setting parent would create a cycle."""
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
```

## API Routes

Create `backend/app/api/projects.py`:

```python
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from pydantic import BaseModel
from app.core.database import get_db
from app.models.project import Project
from app.services.project_service import ProjectService

router = APIRouter(prefix="/api/projects", tags=["projects"])

# Pydantic schemas
class ProjectCreate(BaseModel):
    name: str
    parent_id: Optional[int] = None
    color: str
    description: Optional[str] = None
    default_duration: int = 60
    notification_interval: Optional[int] = None
    is_pinned: bool = False

class ProjectUpdate(BaseModel):
    name: Optional[str] = None
    parent_id: Optional[int] = None
    color: Optional[str] = None
    description: Optional[str] = None
    default_duration: Optional[int] = None
    notification_interval: Optional[int] = None
    is_archived: Optional[bool] = None
    is_pinned: Optional[bool] = None

class ProjectResponse(BaseModel):
    id: int
    name: str
    parent_id: Optional[int]
    color: str
    description: Optional[str]
    default_duration: int
    notification_interval: Optional[int]
    is_archived: bool
    is_pinned: bool

    class Config:
        from_attributes = True

def get_service(db: Session = Depends(get_db)) -> ProjectService:
    return ProjectService(db)

@router.get("/", response_model=List[ProjectResponse])
def list_projects(
    include_archived: bool = False,
    service: ProjectService = Depends(get_service)
):
    return service.get_all(include_archived=include_archived)

@router.get("/pinned", response_model=List[ProjectResponse])
def list_pinned_projects(service: ProjectService = Depends(get_service)):
    return [p for p in service.get_all() if p.is_pinned]

@router.get("/{project_id}", response_model=ProjectResponse)
def get_project(
    project_id: int,
    service: ProjectService = Depends(get_service)
):
    project = service.get_by_id(project_id)
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    return project

@router.post("/", response_model=ProjectResponse, status_code=201)
def create_project(
    data: ProjectCreate,
    service: ProjectService = Depends(get_service)
):
    try:
        return service.create(data.dict())
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.put("/{project_id}", response_model=ProjectResponse)
def update_project(
    project_id: int,
    data: ProjectUpdate,
    service: ProjectService = Depends(get_service)
):
    try:
        return service.update(project_id, data.dict(exclude_unset=True))
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.delete("/{project_id}", status_code=204)
def delete_project(
    project_id: int,
    service: ProjectService = Depends(get_service)
):
    if not service.delete(project_id):
        raise HTTPException(status_code=404, detail="Project not found")
```

## Testing

Create `backend/tests/test_projects.py`:

```python
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_create_project():
    response = client.post("/api/projects/", json={
        "name": "Test Project",
        "color": "#3B82F6",
        "default_duration": 60
    })
    assert response.status_code == 201
    data = response.json()
    assert data["name"] == "Test Project"
    assert data["color"] == "#3B82F6"

def test_list_projects():
    response = client.get("/api/projects/")
    assert response.status_code == 200
    assert isinstance(response.json(), list)

# Add more tests...
```

## Checklist

- [ ] ProjectService created with all CRUD methods
- [ ] Circular reference detection implemented
- [ ] API routes created
- [ ] Pydantic schemas defined
- [ ] Error handling implemented
- [ ] Router included in main.py
- [ ] Basic tests written
- [ ] Tested with curl/Postman
