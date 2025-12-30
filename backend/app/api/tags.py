from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.core.database import get_db

router = APIRouter(prefix="/api/tags", tags=["tags"])


@router.get("/")
async def list_tags(db: Session = Depends(get_db)):
    """List all tags."""
    return {"message": "Tags endpoint - to be implemented"}


@router.post("/")
async def create_tag(db: Session = Depends(get_db)):
    """Create a new tag."""
    return {"message": "Create tag - to be implemented"}


@router.get("/{tag_id}")
async def get_tag(tag_id: int, db: Session = Depends(get_db)):
    """Get a specific tag."""
    return {"message": f"Get tag {tag_id} - to be implemented"}


@router.put("/{tag_id}")
async def update_tag(tag_id: int, db: Session = Depends(get_db)):
    """Update a tag."""
    return {"message": f"Update tag {tag_id} - to be implemented"}


@router.delete("/{tag_id}")
async def delete_tag(tag_id: int, db: Session = Depends(get_db)):
    """Delete a tag."""
    return {"message": f"Delete tag {tag_id} - to be implemented"}
