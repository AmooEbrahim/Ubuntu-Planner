from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.core.database import get_db

router = APIRouter(prefix="/api/projects", tags=["projects"])


@router.get("/")
async def list_projects(db: Session = Depends(get_db)):
    """List all projects."""
    return {"message": "Projects endpoint - to be implemented"}


@router.post("/")
async def create_project(db: Session = Depends(get_db)):
    """Create a new project."""
    return {"message": "Create project - to be implemented"}


@router.get("/{project_id}")
async def get_project(project_id: int, db: Session = Depends(get_db)):
    """Get a specific project."""
    return {"message": f"Get project {project_id} - to be implemented"}


@router.put("/{project_id}")
async def update_project(project_id: int, db: Session = Depends(get_db)):
    """Update a project."""
    return {"message": f"Update project {project_id} - to be implemented"}


@router.delete("/{project_id}")
async def delete_project(project_id: int, db: Session = Depends(get_db)):
    """Delete a project."""
    return {"message": f"Delete project {project_id} - to be implemented"}
