# Settings

Application configuration and customization.

## Overview

Settings system provides:
- General application preferences
- Notification configuration
- Sound customization
- Per-notification-type settings
- Real-time configuration updates

## Settings Storage

### Database Table

```sql
CREATE TABLE settings (
    key_name VARCHAR(100) PRIMARY KEY,
    value_json JSON NOT NULL,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
);
```

### Settings Format

Settings stored as JSON values:
- Simple values: `"en"`, `10`, `true`
- Complex values: `{"sound_enabled": true, "sound_file": "complete.oga"}`

## General Settings

### Language
- **Key:** `language`
- **Type:** string
- **Default:** `"en"`
- **Options:** `"en"` (English), `"fa"` (Persian)
- **Description:** UI language (future feature)

### Default Reminder Interval
- **Key:** `notification_interval_default`
- **Type:** integer (minutes)
- **Default:** `10`
- **Range:** 1-120
- **Description:** How often to remind about unstarted planned work

### Session Poll Interval
- **Key:** `session_poll_interval`
- **Type:** integer (seconds)
- **Default:** `120`
- **Range:** 10-600
- **Description:** How often web interface checks for session updates

## Notification Settings

### Notification Types

Three notification types, each with separate configuration:

1. **Planning Start** (`planning_start`)
   - When scheduled work time arrives
   - Default sound: `complete.oga`
   - Default repeat: 1 time

2. **Session End** (`session_end`)
   - When session time is up (first notification)
   - Default sound: `complete.oga`
   - Default repeat: 1 time

3. **Session Reminder** (`session_reminder`)
   - Repeated reminders after session time is up
   - Default sound: `dialog-warning.oga`
   - Default repeat: 2 times

### Notification Configuration Structure

For each type, two settings:

**Enable Flag:**
- **Key:** `notification_{type}_enabled`
- **Type:** boolean
- **Default:** `true`
- **Description:** Whether to send this notification type

**Configuration:**
- **Key:** `notification_{type}_configuration`
- **Type:** JSON object
- **Structure:**
  ```json
  {
    "sound_enabled": true,
    "sound_file": "complete.oga",
    "sound_repeat": 1
  }
  ```

### Configuration Fields

**sound_enabled** (boolean)
- Whether to play sound with notification
- Default: `true`

**sound_file** (string)
- Sound file name (e.g., `"complete.oga"`)
- Must exist in sounds directory or system sounds
- Default varies by notification type

**sound_repeat** (integer)
- How many times to play sound
- Range: 1-5
- Default: 1 (or 2 for reminders)

## Sound System

### Sound Sources

**System Sounds:**
- Location: `/usr/share/sounds/freedesktop/stereo/`
- Format: `.oga` (Ogg Vorbis)
- Examples: `complete.oga`, `dialog-warning.oga`, `bell.oga`

**Custom Sounds:**
- Location: `sounds/` in project root
- Formats: `.oga`, `.wav`, `.mp3`
- User can add custom sound files

### Available Sounds

Common system sounds:
- `complete.oga` - Completion sound
- `dialog-warning.oga` - Warning/alert
- `message-new-instant.oga` - Message notification
- `bell.oga` - Simple bell
- `dialog-information.oga` - Information

### Sound Guidelines

**Format:** Ogg Vorbis (.oga) recommended
**Duration:** 0.5 - 3 seconds
**Size:** < 100KB
**Volume:** Normalized, non-intrusive

## Settings Page

### Route
`/settings`

### Sections

**General Settings:**
- Language selector
- Default reminder interval (number input)
- Session poll interval (number input)

**Notification Settings:**
For each notification type:
- Enable/disable checkbox
- Sound settings (if enabled):
  - Enable/disable sound checkbox
  - Sound file dropdown (with preview button)
  - Play count selector (1-5 times)

**Actions:**
- Reset to Defaults
- Save Changes

### Features

**Sound Preview:**
- Click "Preview" button to hear sound
- Plays sound once in browser
- No need to save first

**Real-time Validation:**
- Numeric fields validated on input
- Range constraints enforced
- Invalid values highlighted

**Bulk Save:**
- All settings saved atomically
- Success/error feedback shown
- No partial updates

## API Endpoints

### Get All Settings
```
GET /api/settings
```
Returns all settings as key-value object.

### Get Single Setting
```
GET /api/settings/{key_name}
```
Returns value for specific setting.

### Update Setting
```
PUT /api/settings/{key_name}
Body: any (JSON value)
```
Updates a single setting.

### Bulk Update
```
POST /api/settings/bulk-update
Body: {"settings": {"key1": value1, "key2": value2}}
```
Updates multiple settings at once.

### Get Available Sounds
```
GET /api/settings/sounds/available
```
Returns list of available sound files.

### Get Sound File
```
GET /api/settings/sounds/{filename}
```
Serves sound file for preview.

## Usage in Code

### Backend (Python)

```python
from app.models.setting import Setting
import json

# Get setting
setting = db.query(Setting).filter(Setting.key_name == "language").first()
value = json.loads(setting.value_json)

# Update setting
setting.value_json = json.dumps("fa")
db.commit()

# Get notification config
config = db.query(Setting).filter(
    Setting.key_name == "notification_session_end_configuration"
).first()

notification_config = json.loads(config.value_json)
sound_enabled = notification_config.get("sound_enabled", True)
sound_file = notification_config.get("sound_file", "complete.oga")
```

### Frontend (JavaScript)

```javascript
import { useSettingsStore } from '@/stores/settings'

const settingsStore = useSettingsStore()

// Get all settings
const settings = await settingsStore.getAll()
const language = settings.language

// Get single setting
const interval = await settingsStore.get('notification_interval_default')

// Update setting
await settingsStore.update('language', 'fa')

// Update multiple
await settingsStore.updateMultiple({
  language: 'fa',
  notification_interval_default: 15
})
```

## Default Values

When settings don't exist, use these defaults:

```javascript
{
  "language": "en",
  "notification_interval_default": 10,
  "session_poll_interval": 120,

  "notification_planning_start_enabled": true,
  "notification_planning_start_configuration": {
    "sound_enabled": true,
    "sound_file": "complete.oga",
    "sound_repeat": 1
  },

  "notification_session_end_enabled": true,
  "notification_session_end_configuration": {
    "sound_enabled": true,
    "sound_file": "complete.oga",
    "sound_repeat": 1
  },

  "notification_session_reminder_enabled": true,
  "notification_session_reminder_configuration": {
    "sound_enabled": true,
    "sound_file": "dialog-warning.oga",
    "sound_repeat": 2
  }
}
```

## Migration

Initial settings migration:

```sql
-- General settings (already exist)
INSERT INTO settings (key_name, value_json) VALUES
('language', '"en"'),
('notification_interval_default', '10'),
('session_poll_interval', '120');

-- Notification settings (Phase 5)
INSERT INTO settings (key_name, value_json) VALUES
('notification_planning_start_enabled', 'true'),
('notification_planning_start_configuration', '{"sound_enabled": true, "sound_file": "complete.oga", "sound_repeat": 1}'),
('notification_session_end_enabled', 'true'),
('notification_session_end_configuration', '{"sound_enabled": true, "sound_file": "complete.oga", "sound_repeat": 1}'),
('notification_session_reminder_enabled', 'true'),
('notification_session_reminder_configuration', '{"sound_enabled": true, "sound_file": "dialog-warning.oga", "sound_repeat": 2}');
```

## Notes

- Settings changes take effect immediately
- No application restart required
- Notification worker reads settings on each check
- Sound files validated on selection
- Invalid sound files fall back to default
- Settings persisted in database
- JSON format allows flexible value types
