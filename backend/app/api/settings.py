"""Settings API endpoints."""
from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session
from typing import Dict, Any, List
from pydantic import BaseModel

from app.core.database import get_db
from app.models.setting import Setting
from app.services.sound_service import sound_service


router = APIRouter(prefix="/api/settings", tags=["settings"])


class SettingUpdate(BaseModel):
    """Single setting update."""
    key_name: str
    value: Any


class BulkSettingUpdate(BaseModel):
    """Bulk settings update."""
    settings: Dict[str, Any]


@router.get("/")
async def get_all_settings(db: Session = Depends(get_db)) -> Dict[str, Any]:
    """Get all settings as a dictionary.

    Returns:
        Dictionary of all settings with key-value pairs
    """
    settings = db.query(Setting).all()

    result = {}
    for setting in settings:
        # SQLAlchemy JSON column already returns parsed value
        result[setting.key_name] = setting.value_json

    return result


@router.get("/{key_name}")
async def get_setting(key_name: str, db: Session = Depends(get_db)):
    """Get a specific setting.

    Args:
        key_name: The setting key to retrieve

    Returns:
        The setting value

    Raises:
        HTTPException: If setting not found
    """
    setting = db.query(Setting).filter(Setting.key_name == key_name).first()

    if not setting:
        raise HTTPException(status_code=404, detail="Setting not found")

    # SQLAlchemy JSON column already returns parsed value
    return setting.value_json


@router.put("/{key_name}")
async def update_setting(
    key_name: str,
    value: Any,
    db: Session = Depends(get_db)
):
    """Update a setting value.

    Args:
        key_name: The setting key to update
        value: The new value for the setting

    Returns:
        The updated setting
    """
    setting = db.query(Setting).filter(Setting.key_name == key_name).first()

    # SQLAlchemy JSON column handles serialization automatically
    if setting:
        setting.value_json = value
    else:
        setting = Setting(key_name=key_name, value_json=value)
        db.add(setting)

    db.commit()
    db.refresh(setting)

    return {"key_name": key_name, "value": value}


@router.post("/bulk-update")
async def bulk_update_settings(
    updates: BulkSettingUpdate,
    db: Session = Depends(get_db)
):
    """Update multiple settings at once.

    Args:
        updates: Dictionary of settings to update

    Returns:
        Number of settings updated
    """
    for key_name, value in updates.settings.items():
        setting = db.query(Setting).filter(Setting.key_name == key_name).first()

        # SQLAlchemy JSON column handles serialization automatically
        if setting:
            setting.value_json = value
        else:
            setting = Setting(key_name=key_name, value_json=value)
            db.add(setting)

    db.commit()

    return {"updated": len(updates.settings)}


@router.get("/sounds/available")
async def get_available_sounds() -> List[str]:
    """Get list of available sound files.

    Returns:
        List of available sound file names
    """
    return sound_service.get_available_sounds()


@router.get("/sounds/{filename}")
async def get_sound_file(filename: str):
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
