import socket
import tempfile
import json
from pathlib import Path
from typing import Optional
from sqlalchemy.orm import Session
from app.core.config import settings
from app.services.sound_service import sound_service


class NotificationService:
    """Service for sending notifications via existing notification system."""

    def __init__(self):
        self.host = settings.NOTIFICATION_HOST
        self.port = settings.NOTIFICATION_PORT
        self.config_dir = Path.home() / "bin/bash/Ubuntu-Planner/notifications"
        self.config_dir.mkdir(parents=True, exist_ok=True)

    def send_notification(
        self,
        title: str,
        message: str,
        urgency: str = "normal",
        icon: Optional[str] = None,
        timeout: int = 5000,
        notification_type: Optional[str] = None,
        db: Optional[Session] = None
    ) -> bool:
        """Send a notification.

        Args:
            title: Notification title
            message: Notification message
            urgency: Urgency level (low, normal, critical)
            icon: Path to icon file (optional)
            timeout: Display timeout in milliseconds
            notification_type: Type of notification for sound config (planning_start, session_end, session_reminder)
            db: Database session for retrieving settings

        Returns:
            True if notification sent successfully, False otherwise
        """
        try:
            # Create config file content
            config_content = self._create_config(
                title, message, urgency, icon, timeout,
                notification_type, db
            )

            # Write to temporary file
            config_path = self._write_temp_config(config_content)

            # Send to notification service
            success = self._send_to_service(config_path)

            return success

        except Exception as e:
            print(f"Failed to send notification: {e}")
            return False

    def _get_notification_config(self, notification_type: str, db: Session) -> Optional[dict]:
        """Get notification configuration for a type.

        Args:
            notification_type: Type of notification (planning_start, session_end, session_reminder)
            db: Database session

        Returns:
            Configuration dict or None if notifications disabled
        """
        from app.models.setting import Setting

        # Get enabled setting
        enabled_key = f"notification_{notification_type}_enabled"
        enabled_setting = db.query(Setting).filter(
            Setting.key_name == enabled_key
        ).first()

        # SQLAlchemy JSON column already returns parsed value
        if not enabled_setting or not enabled_setting.value_json:
            return None  # Notifications disabled

        # Get configuration
        config_key = f"notification_{notification_type}_configuration"
        config_setting = db.query(Setting).filter(
            Setting.key_name == config_key
        ).first()

        if config_setting:
            return config_setting.value_json

        # Default configuration
        return {
            "sound_enabled": True,
            "sound_file": "complete.oga",
            "sound_repeat": 1
        }

    def _create_config(
        self,
        title: str,
        message: str,
        urgency: str,
        icon: Optional[str],
        timeout: int,
        notification_type: Optional[str] = None,
        db: Optional[Session] = None
    ) -> str:
        """Create notification config content with sound settings.

        Args:
            title: Notification title
            message: Notification message
            urgency: Urgency level
            icon: Icon path
            timeout: Display timeout
            notification_type: Type for sound config
            db: Database session

        Returns:
            Configuration file content
        """
        config = f"""[notification]
title={title}
message={message}
urgency={urgency}
timeout={timeout}
"""
        if icon:
            config += f"icon={icon}\n"

        # Add sound configuration if type and db provided
        if notification_type and db:
            notif_config = self._get_notification_config(notification_type, db)

            if notif_config and notif_config.get('sound_enabled'):
                sound_file = notif_config.get('sound_file', 'complete.oga')
                sound_path = sound_service.get_sound_path(sound_file)

                if sound_path:
                    config += f"sound={sound_path}\n"

                    sound_repeat = notif_config.get('sound_repeat', 1)
                    if sound_repeat > 1:
                        config += f"sound_repeat={sound_repeat}\n"

        return config

    def _write_temp_config(self, content: str) -> str:
        """Write config to temporary file and return path."""
        with tempfile.NamedTemporaryFile(
            mode='w',
            suffix='.conf',
            dir=self.config_dir,
            delete=False
        ) as f:
            f.write(content)
            return f.name

    def _send_to_service(self, config_path: str) -> bool:
        """Send config path to notification service."""
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
                sock.settimeout(2)
                sock.connect((self.host, self.port))
                sock.sendall(f"{config_path}\n".encode('utf-8'))
            return True
        except Exception as e:
            print(f"Failed to connect to notification service: {e}")
            return False

    def cleanup_old_configs(self, max_age_hours: int = 24):
        """Clean up old config files."""
        import time
        now = time.time()
        for config_file in self.config_dir.glob("*.conf"):
            if now - config_file.stat().st_mtime > max_age_hours * 3600:
                config_file.unlink()


# Singleton instance
notification_service = NotificationService()
