# Sound Management System

Sound file management and integration with notification system.

## Overview

Centralized sound system that:
- Stores custom sound files in project directory
- References system sounds from Ubuntu
- Provides sound preview functionality
- Integrates with notification configuration

## Directory Structure

```
Ubuntu-Planner/
├── sounds/                    # Custom sounds directory
│   ├── README.md             # Sound documentation
│   ├── complete.oga          # Default completion sound
│   ├── reminder.oga          # Default reminder sound
│   └── alert.oga             # Default alert sound
└── backend/
    └── app/
        └── services/
            └── sound_service.py  # Sound management
```

## Sound Sources

### 1. System Sounds

Ubuntu system sounds from:
```
/usr/share/sounds/freedesktop/stereo/
```

Common sounds:
- `complete.oga` - Task completion
- `dialog-warning.oga` - Warning/alert
- `message-new-instant.oga` - Notification
- `bell.oga` - Simple bell
- `dialog-information.oga` - Information

### 2. Custom Sounds

Stored in `sounds/` directory at project root.

Supported formats:
- `.oga` (Ogg Vorbis) - Recommended
- `.wav` (Wave)
- `.mp3` (MPEG Audio)

## Initial Sound Setup

### 1. Create Sounds Directory

```bash
mkdir -p sounds
```

### 2. Copy Default Sounds

```bash
# Copy common system sounds to project
cp /usr/share/sounds/freedesktop/stereo/complete.oga sounds/
cp /usr/share/sounds/freedesktop/stereo/dialog-warning.oga sounds/reminder.oga
cp /usr/share/sounds/freedesktop/stereo/bell.oga sounds/alert.oga
```

### 3. Create README

`sounds/README.md`:

```markdown
# Sound Files

This directory contains sound files for Ubuntu Planner notifications.

## Files

- `complete.oga` - Session completion sound
- `reminder.oga` - Session reminder sound
- `alert.oga` - Planning start alert

## Adding Custom Sounds

1. Add your sound file (.oga, .wav, or .mp3) to this directory
2. Restart the backend if running
3. Sound will appear in Settings > Notification Settings

## Recommended Format

- Format: Ogg Vorbis (.oga)
- Sample rate: 44100 Hz
- Channels: Mono or Stereo
- Duration: 0.5 - 3 seconds

## Sound Guidelines

- Keep files small (< 100KB)
- Use short, non-intrusive sounds
- Test volume levels before use
```

## Sound Service Implementation

### Backend Service

Create `backend/app/services/sound_service.py`:

```python
from pathlib import Path
from typing import List, Optional
import os

class SoundService:
    """Service for managing sound files."""

    def __init__(self):
        self.project_root = Path(__file__).parent.parent.parent.parent
        self.custom_sounds_dir = self.project_root / "sounds"
        self.system_sounds_dir = Path("/usr/share/sounds/freedesktop/stereo")

        # Ensure custom sounds directory exists
        self.custom_sounds_dir.mkdir(exist_ok=True)

    def get_available_sounds(self) -> List[str]:
        """Get list of all available sound files."""
        sounds = []

        # System sounds
        if self.system_sounds_dir.exists():
            sounds.extend([
                f.name for f in self.system_sounds_dir.glob("*.oga")
            ])

        # Custom sounds
        if self.custom_sounds_dir.exists():
            for ext in ['*.oga', '*.wav', '*.mp3']:
                sounds.extend([
                    f.name for f in self.custom_sounds_dir.glob(ext)
                ])

        # Remove duplicates and sort
        return sorted(set(sounds))

    def get_sound_path(self, filename: str) -> Optional[Path]:
        """Get full path to a sound file."""
        # Check custom sounds first
        custom_path = self.custom_sounds_dir / filename
        if custom_path.exists():
            return custom_path

        # Check system sounds
        system_path = self.system_sounds_dir / filename
        if system_path.exists():
            return system_path

        return None

    def validate_sound_file(self, filename: str) -> bool:
        """Check if sound file exists."""
        return self.get_sound_path(filename) is not None

    def get_default_sounds(self) -> dict:
        """Get default sound configuration."""
        return {
            "planning_start": "complete.oga",
            "session_end": "complete.oga",
            "session_reminder": "dialog-warning.oga"
        }

sound_service = SoundService()
```

## Integration with Notification Service

### Update Notification Service

Modify `backend/app/services/notification_service.py`:

```python
from app.services.sound_service import sound_service
from app.models.setting import Setting
import json

class NotificationService:
    # ... existing code ...

    def _get_notification_config(self, notification_type: str, db) -> dict:
        """Get notification configuration for a type."""
        # Get enabled setting
        enabled_key = f"notification_{notification_type}_enabled"
        enabled_setting = db.query(Setting).filter(
            Setting.key_name == enabled_key
        ).first()

        if not enabled_setting or not json.loads(enabled_setting.value_json):
            return None  # Notifications disabled

        # Get configuration
        config_key = f"notification_{notification_type}_configuration"
        config_setting = db.query(Setting).filter(
            Setting.key_name == config_key
        ).first()

        if config_setting:
            return json.loads(config_setting.value_json)

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
        notification_type: str,
        db
    ) -> str:
        """Create notification config content with sound settings."""
        config = f"""[notification]
title={title}
message={message}
urgency={urgency}
timeout={timeout}
"""
        if icon:
            config += f"icon={icon}\n"

        # Add sound configuration
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

    def send_planning_notification(self, title: str, message: str, db):
        """Send planning start notification."""
        config = self._create_config(
            title, message, "normal", None, 5000,
            "planning_start", db
        )
        # ... send logic ...

    def send_session_end_notification(self, title: str, message: str, db):
        """Send session end notification."""
        config = self._create_config(
            title, message, "normal", None, 5000,
            "session_end", db
        )
        # ... send logic ...

    def send_session_reminder_notification(self, title: str, message: str, db):
        """Send session reminder notification."""
        config = self._create_config(
            title, message, "normal", None, 5000,
            "session_reminder", db
        )
        # ... send logic ...
```

## Sound Preview API

Add to `backend/app/api/settings.py`:

```python
from fastapi.responses import FileResponse

@router.get("/sounds/{filename}")
async def get_sound_file(filename: str):
    """Serve a sound file for preview."""
    from app.services.sound_service import sound_service

    sound_path = sound_service.get_sound_path(filename)

    if not sound_path:
        raise HTTPException(status_code=404, detail="Sound file not found")

    return FileResponse(
        sound_path,
        media_type="audio/ogg"  # Adjust based on file type
    )
```

## Frontend Sound Preview

In Settings component, add sound preview:

```javascript
function previewSound(soundFile) {
  const audio = new Audio(`/api/settings/sounds/${soundFile}`)
  audio.play().catch(err => {
    console.error('Failed to play sound:', err)
    alert('Failed to play sound preview')
  })
}
```

## Database Migration

Add default notification settings:

```sql
INSERT INTO settings (key_name, value_json) VALUES
('notification_planning_start_enabled', 'true'),
('notification_planning_start_configuration', '{"sound_enabled": true, "sound_file": "complete.oga", "sound_repeat": 1}'),
('notification_session_end_enabled', 'true'),
('notification_session_end_configuration', '{"sound_enabled": true, "sound_file": "complete.oga", "sound_repeat": 1}'),
('notification_session_reminder_enabled', 'true'),
('notification_session_reminder_configuration', '{"sound_enabled": true, "sound_file": "dialog-warning.oga", "sound_repeat": 2}');
```

## Setup Script

Create `setup-sounds.sh`:

```bash
#!/bin/bash

# Create sounds directory
mkdir -p sounds

# Copy default sounds from system
echo "Copying default sounds..."

if [ -f "/usr/share/sounds/freedesktop/stereo/complete.oga" ]; then
    cp /usr/share/sounds/freedesktop/stereo/complete.oga sounds/
    echo "✓ Copied complete.oga"
fi

if [ -f "/usr/share/sounds/freedesktop/stereo/dialog-warning.oga" ]; then
    cp /usr/share/sounds/freedesktop/stereo/dialog-warning.oga sounds/reminder.oga
    echo "✓ Copied reminder.oga"
fi

if [ -f "/usr/share/sounds/freedesktop/stereo/bell.oga" ]; then
    cp /usr/share/sounds/freedesktop/stereo/bell.oga sounds/alert.oga
    echo "✓ Copied alert.oga"
fi

echo "Sound setup complete!"
echo "Custom sounds directory: $(pwd)/sounds"
```

Make executable:
```bash
chmod +x setup-sounds.sh
```

## Checklist

- [ ] Sounds directory created
- [ ] Default sounds copied
- [ ] README.md in sounds directory
- [ ] Sound service implemented
- [ ] Available sounds API endpoint
- [ ] Sound file serving endpoint
- [ ] Frontend preview working
- [ ] Integration with notification service
- [ ] Database migration for settings
- [ ] Setup script created

## Notes

- Sounds served via backend API for security
- Frontend cannot access filesystem directly
- System sounds not copied, referenced in place
- Custom sounds copied to project directory
- Sound repeat plays the same sound multiple times with short pause
