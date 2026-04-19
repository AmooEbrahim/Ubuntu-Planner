import socket
import tempfile
from pathlib import Path
from typing import Optional
from app.core.config import settings
from app.services.sound_service import sound_service
from app.services.setting_service import SettingService
from app.core.database import SessionLocal


class NotificationService:
    """Service for sending notifications via existing notification system."""

    def __init__(self):
        self.host = settings.NOTIFICATION_HOST
        self.port = settings.NOTIFICATION_PORT
        self.config_dir = settings.notification_config_dir
        self.config_dir.mkdir(parents=True, exist_ok=True)

    def send_notification(
        self,
        title: str,
        message: str,
        urgency: str = "normal",
        icon: Optional[str] = None,
        timeout: int = 5000,
        notification_type: Optional[str] = None
    ) -> bool:
        """Send a notification.

        Args:
            title: Notification title
            message: Notification message
            urgency: Urgency level (low, normal, critical)
            icon: Path to icon file (optional)
            timeout: Display timeout in milliseconds
            notification_type: Type of notification for sound config (planning_start, session_end, session_reminder)

        Returns:
            True if notification sent successfully, False otherwise
        """
        try:
            config_content = self._create_config(
                title, message, urgency, icon, timeout, notification_type
            )

            config_path = self._write_temp_config(config_content)
            success = self._send_to_service(config_path)

            return success

        except Exception as e:
            print(f"Failed to send notification: {e}")
            return False

    def _create_config(
        self,
        title: str,
        message: str,
        urgency: str,
        icon: Optional[str],
        timeout: int,
        notification_type: Optional[str] = None
    ) -> str:
        """Create notification config content with sound settings.

        Args:
            title: Notification title
            message: Notification message
            urgency: Urgency level
            icon: Icon path
            timeout: Display timeout
            notification_type: Type for sound config

        Returns:
            Configuration file content in proper INI format
        """
        config_lines = [
            "[notification]",
            "notification_enabled=true",
            f"title={title}",
            f"body={message}",
        ]

        if icon:
            config_lines.append(f"icon={icon}")

        config_lines.extend([
            f"urgency={urgency}",
            f"timeout={timeout}",
            "transient=true",
            ""
        ])

        if notification_type:
            notif_config = self._get_notification_config(notification_type)

            if notif_config and notif_config.get('sound_enabled'):
                sound_file = notif_config.get('sound_file', 'complete.oga')
                sound_path = sound_service.get_sound_path(sound_file)

                if sound_path:
                    sound_repeat = notif_config.get('sound_repeat', 1)
                    config_lines.extend([
                        "[sound]",
                        "sound_enabled=true",
                        f"file={sound_path}",
                        "play=true",
                        f"repeat={sound_repeat}",
                        "sleep=1"
                    ])

        return "\n".join(config_lines) + "\n"

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
