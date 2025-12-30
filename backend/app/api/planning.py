from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.core.database import get_db

router = APIRouter(prefix="/api/planning", tags=["planning"])


@router.get("/")
async def list_planning(db: Session = Depends(get_db)):
    """List all planning items."""
    return {"message": "Planning endpoint - to be implemented"}


@router.post("/")
async def create_planning(db: Session = Depends(get_db)):
    """Create a new planning item."""
    return {"message": "Create planning - to be implemented"}


@router.get("/{planning_id}")
async def get_planning(planning_id: int, db: Session = Depends(get_db)):
    """Get a specific planning item."""
    return {"message": f"Get planning {planning_id} - to be implemented"}


@router.put("/{planning_id}")
async def update_planning(planning_id: int, db: Session = Depends(get_db)):
    """Update a planning item."""
    return {"message": f"Update planning {planning_id} - to be implemented"}


@router.delete("/{planning_id}")
async def delete_planning(planning_id: int, db: Session = Depends(get_db)):
    """Delete a planning item."""
    return {"message": f"Delete planning {planning_id} - to be implemented"}
