import socket
import tempfile
from pathlib import Path
from typing import Optional
from app.core.config import settings


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
        timeout: int = 5000
    ) -> bool:
        """Send a notification.

        Args:
            title: Notification title
            message: Notification message
            urgency: Urgency level (low, normal, critical)
            icon: Path to icon file (optional)
            timeout: Display timeout in milliseconds

        Returns:
            True if notification sent successfully, False otherwise
        """
        try:
            # Create config file content
            config_content = self._create_config(title, message, urgency, icon, timeout)

            # Write to temporary file
            config_path = self._write_temp_config(config_content)

            # Send to notification service
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
        timeout: int
    ) -> str:
        """Create notification config content."""
        config = f"""[notification]
title={title}
message={message}
urgency={urgency}
timeout={timeout}
"""
        if icon:
            config += f"icon={icon}\n"

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
