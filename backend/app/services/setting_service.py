"""Setting service for managing application settings."""
from typing import Any, Dict, List, Optional
from sqlalchemy.orm import Session
from app.models.setting import Setting


class SettingService:
    """Service for managing application settings."""

    def __init__(self, db: Session):
        """Initialize setting service.

        Args:
            db: Database session
        """
        self.db = db

    def get_all(self) -> Dict[str, Any]:
        """Get all settings as a dictionary.

        Returns:
            Dictionary of all settings with key-value pairs
        """
        settings = self.db.query(Setting).all()
        return {setting.key_name: setting.value_json for setting in settings}

    def get_by_key(self, key_name: str) -> Optional[Any]:
        """Get a specific setting by key.

        Args:
            key_name: The setting key to retrieve

        Returns:
            The setting value or None if not found
        """
        setting = self.db.query(Setting).filter(Setting.key_name == key_name).first()
        return setting.value_json if setting else None

    def set(self, key_name: str, value: Any) -> Setting:
        """Update or create a setting.

        Args:
            key_name: The setting key
            value: The value to set

        Returns:
            The updated or created setting
        """
        setting = self.db.query(Setting).filter(Setting.key_name == key_name).first()

        if setting:
            setting.value_json = value
        else:
            setting = Setting(key_name=key_name, value_json=value)
            self.db.add(setting)

        self.db.commit()
        self.db.refresh(setting)
        return setting

    def bulk_update(self, settings: Dict[str, Any]) -> int:
        """Update multiple settings at once.

        Args:
            settings: Dictionary of settings to update

        Returns:
            Number of settings updated
        """
        for key_name, value in settings.items():
            self.set(key_name, value)

        return len(settings)

    def delete(self, key_name: str) -> bool:
        """Delete a setting.

        Args:
            key_name: The setting key to delete

        Returns:
            True if deleted, False if not found
        """
        setting = self.db.query(Setting).filter(Setting.key_name == key_name).first()
        if not setting:
            return False

        self.db.delete(setting)
        self.db.commit()
        return True

    def get_notification_config(self, notification_type: str) -> Optional[dict]:
        """Get notification configuration for a type.

        Args:
            notification_type: Type of notification (planning_start, session_end, session_reminder)

        Returns:
            Configuration dict or None if notifications disabled
        """
        enabled_key = f"notification_{notification_type}_enabled"
        enabled_value = self.get_by_key(enabled_key)

        if not enabled_value:
            return None

        config_key = f"notification_{notification_type}_configuration"
        config_value = self.get_by_key(config_key)

        if config_value:
            return config_value

        return {
            "sound_enabled": True,
            "sound_file": "complete.oga",
            "sound_repeat": 1
        }