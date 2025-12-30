# Notification Service Integration

Integration with existing notification service for Ubuntu Planner.
Note for who they see this: I will share the notification service on github later and you could use that.

## Overview

Ubuntu Planner uses an existing notification service that:
- Listens on `localhost:52346`
- Accepts notification config file paths
- Displays notifications based on config

## How It Works

### Architecture

```
Ubuntu Planner → Creates temp config file → Sends path to port 52346 → Service shows notification
```

### Config File Format

Based on the example at `./example-notification.conf`, create similar configs for our notifications.

**Example Config File:**
```ini
[notification]
title=Session Complete
message=Time to take a break!
urgency=normal
icon=/path/to/icon.png
timeout=5000
```

(Note: Actual format should match the existing service's expected format. Check the example file for exact format.)

## Implementation

### Python Helper Function

Create `backend/app/services/notification_service.py`:

```python
import socket
import tempfile
import os
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
        """Create notification config content.

        Note: Format should match existing service's expected format.
        Check /home/ebrhaim/bin/bash/v2ray/notification_connected.conf for reference.
        """
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
        finally:
            # Clean up temp file after a delay (or keep for debugging)
            # For now, keep files for debugging
            pass

    def cleanup_old_configs(self, max_age_hours: int = 24):
        """Clean up old config files."""
        import time
        now = time.time()
        for config_file in self.config_dir.glob("*.conf"):
            if now - config_file.stat().st_mtime > max_age_hours * 3600:
                config_file.unlink()


# Singleton instance
notification_service = NotificationService()
```

### Usage Examples

#### Session End Notification

```python
from app.services.notification_service import notification_service

def notify_session_end(project_name: str, duration: int):
    """Notify when session time is up."""
    notification_service.send_notification(
        title=f"Session Complete: {project_name}",
        message=f"Time is up! You've worked for {duration} minutes. Consider taking a break.",
        urgency="normal"
    )
```

#### Planning Start Notification

```python
def notify_planning_start(project_name: str, description: str = ""):
    """Notify when it's time to start planned work."""
    message = f"Time to start: {project_name}"
    if description:
        message += f"\n{description}"

    notification_service.send_notification(
        title="Scheduled Work",
        message=message,
        urgency="normal"
    )
```

#### Critical Planning Notification

```python
def notify_critical_planning(project_name: str):
    """Notify for critical priority planning."""
    notification_service.send_notification(
        title=f"CRITICAL: {project_name}",
        message=f"Important scheduled work is about to start!",
        urgency="critical"
    )
```

### Background Worker Integration

Create `backend/app/tasks/notification_worker.py`:

```python
import asyncio
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from app.core.database import SessionLocal
from app.models.planning import Planning
from app.models.session import Session as WorkSession
from app.services.notification_service import notification_service

class NotificationWorker:
    """Background worker for checking and sending notifications."""

    def __init__(self):
        self.running = False
        self.check_interval = 60  # Check every minute

    async def start(self):
        """Start the notification worker."""
        self.running = True
        print("Notification worker started")

        while self.running:
            try:
                await self.check_notifications()
            except Exception as e:
                print(f"Error in notification worker: {e}")

            await asyncio.sleep(self.check_interval)

    async def stop(self):
        """Stop the notification worker."""
        self.running = False
        print("Notification worker stopped")

    async def check_notifications(self):
        """Check for notifications that need to be sent."""
        db = SessionLocal()
        try:
            await self._check_planning_notifications(db)
            await self._check_session_notifications(db)
        finally:
            db.close()

    async def _check_planning_notifications(self, db: Session):
        """Check for planning that should trigger notifications."""
        now = datetime.now()
        window_start = now - timedelta(minutes=5)
        window_end = now + timedelta(minutes=5)

        # Get planning in current time window
        planning_list = db.query(Planning).filter(
            Planning.scheduled_start >= window_start,
            Planning.scheduled_start <= window_end
        ).all()

        for plan in planning_list:
            # Check if already started
            session = db.query(WorkSession).filter(
                WorkSession.planning_id == plan.id
            ).first()

            if not session:
                # Check if any session started after plan start
                any_session = db.query(WorkSession).filter(
                    WorkSession.start_time >= plan.scheduled_start,
                    WorkSession.end_time.is_(None)
                ).first()

                if not any_session:
                    # Send notification
                    self._send_planning_notification(plan)

    async def _check_session_notifications(self, db: Session):
        """Check for active sessions that should trigger notifications."""
        active_session = db.query(WorkSession).filter(
            WorkSession.end_time.is_(None)
        ).first()

        if active_session and not active_session.notification_disabled:
            elapsed = (datetime.now() - active_session.start_time).total_seconds() / 60

            if elapsed >= active_session.planned_duration:
                # Check if notification should be sent
                overtime = elapsed - active_session.planned_duration

                # Get notification interval
                interval = 10  # Default
                if active_session.project and active_session.project.notification_interval:
                    interval = active_session.project.notification_interval

                # Send if at interval boundary
                if overtime % interval < 1:  # Within 1 minute of interval
                    self._send_session_notification(active_session, overtime)

    def _send_planning_notification(self, plan: Planning):
        """Send notification for planning start."""
        urgency = "critical" if plan.priority == "critical" else "normal"

        message = f"Time to start: {plan.project.name}"
        if plan.description:
            message += f"\n{plan.description}"

        notification_service.send_notification(
            title="Scheduled Work",
            message=message,
            urgency=urgency
        )

    def _send_session_notification(self, session: WorkSession, overtime: float):
        """Send notification for session end/overtime."""
        project_name = session.project.name if session.project else "Session"

        if overtime < 1:
            # First notification (time's up)
            message = f"Time is up! You've worked for {session.planned_duration} minutes. Consider taking a break."
        else:
            # Repeated notification
            message = f"Still working? You're {int(overtime)} minutes over planned time.\n"
            message += f"Planned: {session.planned_duration} min, Elapsed: {int(overtime + session.planned_duration)} min"

        notification_service.send_notification(
            title=f"Session: {project_name}",
            message=message,
            urgency="normal"
        )


# Singleton instance
notification_worker = NotificationWorker()
```

### Integration with FastAPI

In `backend/app/main.py`:

```python
from contextlib import asynccontextmanager
from app.tasks.notification_worker import notification_worker

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    asyncio.create_task(notification_worker.start())
    yield
    # Shutdown
    await notification_worker.stop()

app = FastAPI(lifespan=lifespan, ...)
```

## Testing

### Test Notification Service

Create `backend/test_notification.py`:

```python
from app.services.notification_service import notification_service

def test_notification():
    """Test sending a notification."""
    success = notification_service.send_notification(
        title="Test Notification",
        message="This is a test message from Ubuntu Planner",
        urgency="normal"
    )
    print(f"Notification sent: {success}")

if __name__ == "__main__":
    test_notification()
```

Run:
```bash
cd backend
python test_notification.py
```

### Verify Config File Format

1. Check the example config:
```bash
cat /home/ebrhaim/bin/bash/v2ray/notification_connected.conf
```

2. Ensure our config format matches
3. Test with the actual notification service

## Troubleshooting

### Issue: Notification not appearing
**Checks:**
- Is notification service running?
- Is it listening on port 52346?
- Check config file format
- Check logs

### Issue: Connection refused
**Checks:**
- Verify NOTIFICATION_PORT in .env
- Ensure notification service is started
- Check firewall settings

### Issue: Wrong format
**Solution:**
- Compare with example config file
- Adjust `_create_config()` method to match exact format

## Cleanup

Periodically clean up old config files:

```python
# In a scheduled task or on app start
notification_service.cleanup_old_configs(max_age_hours=24)
```

## Future Enhancements

- Custom notification sounds per priority
- Notification action buttons (Start Session, Snooze)
- Persistent notification history
- Desktop notification fallback if service unavailable
