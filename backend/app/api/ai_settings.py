"""AI settings API."""
from typing import List

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.schemas.ai_settings import (
    AISettingsResponse,
    AISettingsUpdate,
    ToolDescriptor,
)
from app.services.ai_settings_service import AISettingsService
from app.services.ai.tools.registry import (
    DEFAULT_TIER_LEVELS,
    all_tools,
)


router = APIRouter(prefix="/api/ai-settings", tags=["ai-settings"])


def get_service(db: Session = Depends(get_db)) -> AISettingsService:
    return AISettingsService(db)


@router.get("/", response_model=AISettingsResponse)
async def get_settings(service: AISettingsService = Depends(get_service)):
    return service.get_config()


@router.put("/", response_model=AISettingsResponse)
async def update_settings(
    data: AISettingsUpdate,
    service: AISettingsService = Depends(get_service),
):
    return service.update_config(data.model_dump(exclude_unset=True))


@router.get("/tools", response_model=List[ToolDescriptor])
async def list_tools_endpoint():
    """Introspect the tool registry. The settings UI uses this to render permission toggles."""
    return [
        ToolDescriptor(
            name=t.name,
            description=t.description,
            permission_tier=t.permission_tier,
            default_level=DEFAULT_TIER_LEVELS[t.permission_tier],
        )
        for t in all_tools()
    ]
