"""Settings API endpoints."""
from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session
from typing import Dict, Any, List
from pydantic import BaseModel
from app.core.database import get_db
from app.services.setting_service import SettingService
from app.services.sound_service import sound_service


router = APIRouter(prefix="/api/settings", tags=["settings"])


class SettingUpdate(BaseModel):
    """Single setting update."""
    key_name: str
    value: Any


class BulkSettingUpdate(BaseModel):
    """Bulk settings update."""
    settings: Dict[str, Any]


def get_service(db: Session = Depends(get_db)) -> SettingService:
    """Get setting service instance.

    Args:
        db: Database session

    Returns:
        SettingService instance
    """
    return SettingService(db)


@router.get("/")
async def get_all_settings(service: SettingService = Depends(get_service)) -> Dict[str, Any]:
    """Get all settings as a dictionary.

    Returns:
        Dictionary of all settings with key-value pairs
    """
    return service.get_all()


@router.get("/{key_name}")
async def get_setting(
    key_name: str,
    service: SettingService = Depends(get_service)
) -> Any:
    """Get a specific setting.

    Args:
        key_name: The setting key to retrieve
        service: Setting service instance

    Returns:
        The setting value

    Raises:
        HTTPException: If setting not found
    """
    value = service.get_by_key(key_name)
    if value is None:
        raise HTTPException(status_code=404, detail="Setting not found")
    return value


@router.put("/{key_name}")
async def update_setting(
    key_name: str,
    value: Any,
    service: SettingService = Depends(get_service)
) -> Dict[str, Any]:
    """Update a setting value.

    Args:
        key_name: The setting key to update
        value: The new value for the setting
        service: Setting service instance

    Returns:
        The updated setting
    """
    setting = service.set(key_name, value)
    return {"key_name": setting.key_name, "value": setting.value_json}


@router.post("/bulk-update")
async def bulk_update_settings(
    updates: BulkSettingUpdate,
    service: SettingService = Depends(get_service)
):
    """Update multiple settings at once.

    Args:
        updates: Dictionary of settings to update
        service: Setting service instance

    Returns:
        Number of settings updated
    """
    updated = service.bulk_update(updates.settings)
    return {"updated": updated}


@router.get("/sounds/available")
async def get_available_sounds() -> List[str]:
    """Get list of available sound files.

    Returns:
        List of available sound file names
    """
    return sound_service.get_available_sounds()


@router.get("/sounds/{filename}")
async def get_sound_file(filename: str) -> FileResponse:
    """Serve a sound file for preview.

    Args:
        filename: Name of the sound file

    Returns:
        Sound file response

    Raises:
        HTTPException: If sound file not found
    """
    sound_path = sound_service.get_sound_path(filename)

    if not sound_path:
        raise HTTPException(status_code=404, detail="Sound file not found")

    # Determine media type based on file extension
    ext = sound_path.suffix.lower()
    media_type_map = {
        '.oga': 'audio/ogg',
        '.ogg': 'audio/ogg',
        '.wav': 'audio/wav',
        '.mp3': 'audio/mpeg'
    }
    media_type = media_type_map.get(ext, 'audio/ogg')

    return FileResponse(
        sound_path,
        media_type=media_type
    )
