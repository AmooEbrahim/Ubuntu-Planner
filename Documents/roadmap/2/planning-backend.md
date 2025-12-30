# Planning Backend Implementation

Backend API for scheduling and planning management.

## Models

Planning model already created in Phase 0. Verify:
- `backend/app/models/planning.py`
- `backend/app/models/planning_tags.py` (many-to-many table)

## Service Layer

Create `backend/app/services/planning_service.py`:

```python
from datetime import datetime, date
from typing import List, Optional
from sqlalchemy.orm import Session
from app.models.planning import Planning
from app.models.tag import Tag

class PlanningService:
    def __init__(self, db: Session):
        self.db = db

    def get_by_date(self, target_date: date) -> List[Planning]:
        """Get all planning for a specific date."""
        start_of_day = datetime.combine(target_date, datetime.min.time())
        end_of_day = datetime.combine(target_date, datetime.max.time())

        return self.db.query(Planning).filter(
            Planning.scheduled_start >= start_of_day,
            Planning.scheduled_start <= end_of_day
        ).order_by(Planning.scheduled_start).all()

    def check_overlap(
        self,
        scheduled_start: datetime,
        scheduled_end: datetime,
        exclude_id: Optional[int] = None
    ) -> bool:
        """Check if there's an overlap with existing planning."""
        query = self.db.query(Planning).filter(
            Planning.scheduled_start < scheduled_end,
            Planning.scheduled_end > scheduled_start
        )

        if exclude_id:
            query = query.filter(Planning.id != exclude_id)

        return query.first() is not None

    def validate_same_day(self, scheduled_start: datetime, scheduled_end: datetime) -> bool:
        """Validate that start and end are on the same day."""
        return scheduled_start.date() == scheduled_end.date()

    def create(self, planning_data: dict) -> Planning:
        """Create new planning."""
        # Validation
        if not self.validate_same_day(
            planning_data['scheduled_start'],
            planning_data['scheduled_end']
        ):
            raise ValueError("Planning must be within the same day")

        if self.check_overlap(
            planning_data['scheduled_start'],
            planning_data['scheduled_end']
        ):
            raise ValueError("Planning overlaps with existing planning")

        # Extract tags if provided
        tag_ids = planning_data.pop('tag_ids', [])

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
        """Update planning."""
        planning = self.db.query(Planning).filter(Planning.id == planning_id).first()
        if not planning:
            raise ValueError("Planning not found")

        # If changing times, validate
        new_start = planning_data.get('scheduled_start', planning.scheduled_start)
        new_end = planning_data.get('scheduled_end', planning.scheduled_end)

        if not self.validate_same_day(new_start, new_end):
            raise ValueError("Planning must be within the same day")

        if self.check_overlap(new_start, new_end, exclude_id=planning_id):
            raise ValueError("Planning overlaps with existing planning")

        # Extract tags if provided
        tag_ids = planning_data.pop('tag_ids', None)

        # Update fields
        for key, value in planning_data.items():
            setattr(planning, key, value)

        # Update tags if provided
        if tag_ids is not None:
            tags = self.db.query(Tag).filter(Tag.id.in_(tag_ids)).all()
            planning.tags = tags

        self.db.commit()
        self.db.refresh(planning)
        return planning

    def delete(self, planning_id: int) -> bool:
        """Delete planning."""
        planning = self.db.query(Planning).filter(Planning.id == planning_id).first()
        if not planning:
            return False

        self.db.delete(planning)
        self.db.commit()
        return True
```

## API Routes

Create `backend/app/api/planning.py`:

```python
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import date, datetime
from pydantic import BaseModel
from app.core.database import get_db
from app.services.planning_service import PlanningService

router = APIRouter(prefix="/api/planning", tags=["planning"])

class PlanningCreate(BaseModel):
    project_id: int
    scheduled_start: datetime
    scheduled_end: datetime
    priority: str = "medium"
    description: Optional[str] = None
    tag_ids: List[int] = []

class PlanningUpdate(BaseModel):
    project_id: Optional[int] = None
    scheduled_start: Optional[datetime] = None
    scheduled_end: Optional[datetime] = None
    priority: Optional[str] = None
    description: Optional[str] = None
    tag_ids: Optional[List[int]] = None

class PlanningResponse(BaseModel):
    id: int
    project_id: int
    scheduled_start: datetime
    scheduled_end: datetime
    priority: str
    description: Optional[str]
    # Include project and tags in response

    class Config:
        from_attributes = True

def get_service(db: Session = Depends(get_db)) -> PlanningService:
    return PlanningService(db)

@router.get("/", response_model=List[PlanningResponse])
def list_planning(
    date: Optional[date] = Query(None),
    service: PlanningService = Depends(get_service)
):
    """List planning, optionally filtered by date."""
    if date:
        return service.get_by_date(date)
    # Return all or recent if no filter
    return []  # Implement as needed

@router.get("/today", response_model=List[PlanningResponse])
def today_planning(service: PlanningService = Depends(get_service)):
    """Get today's planning."""
    return service.get_by_date(date.today())

@router.post("/", response_model=PlanningResponse, status_code=201)
def create_planning(
    data: PlanningCreate,
    service: PlanningService = Depends(get_service)
):
    try:
        return service.create(data.dict())
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.put("/{planning_id}", response_model=PlanningResponse)
def update_planning(
    planning_id: int,
    data: PlanningUpdate,
    service: PlanningService = Depends(get_service)
):
    try:
        return service.update(planning_id, data.dict(exclude_unset=True))
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.delete("/{planning_id}", status_code=204)
def delete_planning(
    planning_id: int,
    service: PlanningService = Depends(get_service)
):
    if not service.delete(planning_id):
        raise HTTPException(status_code=404, detail="Planning not found")
```

## Checklist

- [ ] PlanningService created
- [ ] Overlap detection implemented
- [ ] Same-day validation implemented
- [ ] API routes created
- [ ] Tag relationships handled
- [ ] Router included in main.py
- [ ] Tested overlap detection
- [ ] Tested same-day validation
