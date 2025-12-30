# Settings Management

Comprehensive settings page for general configuration and notification customization.

## Overview

Settings page provides:
- General application settings
- Notification configuration per type
- Sound selection and preview
- Real-time preview of changes

## Route

**Path:** `/settings`

## Settings Structure

### Database Schema

Settings stored in `settings` table:

```sql
CREATE TABLE settings (
    key_name VARCHAR(100) PRIMARY KEY,
    value_json JSON NOT NULL,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
);
```

### Existing Settings

| Key | Type | Default | Description |
|-----|------|---------|-------------|
| `language` | string | "en" | UI language |
| `notification_interval_default` | int | 10 | Default reminder interval (minutes) |
| `session_poll_interval` | int | 120 | Frontend polling interval (seconds) |

### New Settings (Phase 5)

**Planning Start Notification:**
- `notification_planning_start_enabled` - boolean
- `notification_planning_start_configuration` - JSON

**Session End Notification:**
- `notification_session_end_enabled` - boolean
- `notification_session_end_configuration` - JSON

**Session Reminder Notification:**
- `notification_session_reminder_enabled` - boolean
- `notification_session_reminder_configuration` - JSON

### Notification Configuration JSON Structure

```json
{
  "sound_enabled": true,
  "sound_file": "complete.oga",
  "sound_repeat": 1
}
```

**Fields:**
- `sound_enabled` (boolean): Whether to play sound
- `sound_file` (string): Sound file name or path
- `sound_repeat` (int): How many times to play (1-5)

## UI Layout

### Page Structure

```
┌─────────────────────────────────────────┐
│ Settings                                │
├─────────────────────────────────────────┤
│                                         │
│ General Settings                        │
│ ├─ Language                             │
│ ├─ Default Reminder Interval            │
│ └─ Session Poll Interval                │
│                                         │
│ Notification Settings                   │
│ ├─ Planning Start                       │
│ ├─ Session End                          │
│ └─ Session Reminder                     │
│                                         │
│ [ Reset to Defaults ]  [ Save Changes ] │
└─────────────────────────────────────────┘
```

### General Settings Section

```
┌─────────────────────────────────────────┐
│ General Settings                        │
├─────────────────────────────────────────┤
│                                         │
│ Language                                │
│ ┌─────────────────────────────────────┐ │
│ │ English ▼                           │ │
│ └─────────────────────────────────────┘ │
│                                         │
│ Default Reminder Interval (minutes)     │
│ ┌─────────────────────────────────────┐ │
│ │ 10                                  │ │
│ └─────────────────────────────────────┘ │
│ How often to remind about unstarted     │
│ planned work.                           │
│                                         │
│ Session Poll Interval (seconds)         │
│ ┌─────────────────────────────────────┐ │
│ │ 120                                 │ │
│ └─────────────────────────────────────┘ │
│ How often to check for session updates. │
└─────────────────────────────────────────┘
```

### Notification Settings Section

For each notification type (Planning Start, Session End, Session Reminder):

```
┌─────────────────────────────────────────┐
│ Planning Start Notification             │
├─────────────────────────────────────────┤
│                                         │
│ ☑ Enable notifications                 │
│                                         │
│ Sound Settings                          │
│ ├─ ☑ Play sound                        │
│ │                                       │
│ │  Sound File                           │
│ │  ┌───────────────────────────────┐   │
│ │  │ complete.oga ▼                │   │
│ │  └───────────────────────────────┘   │
│ │  [▶ Preview]                         │
│ │                                       │
│ │  Play Count                           │
│ │  ┌───────────────────────────────┐   │
│ │  │ 1 time ▼                      │   │
│ │  └───────────────────────────────┘   │
│ │                                       │
│ └─                                      │
└─────────────────────────────────────────┘
```

## Implementation

### Frontend Component

Create `frontend/src/views/Settings.vue`:

```vue
<script setup>
import { ref, reactive, onMounted } from 'vue'
import { useSettingsStore } from '@/stores/settings'

const settingsStore = useSettingsStore()

const general = reactive({
  language: 'en',
  notification_interval_default: 10,
  session_poll_interval: 120
})

const notificationTypes = [
  {
    key: 'planning_start',
    label: 'Planning Start Notification',
    description: 'When scheduled work time arrives'
  },
  {
    key: 'session_end',
    label: 'Session End Notification',
    description: 'When session time is up (first notification)'
  },
  {
    key: 'session_reminder',
    label: 'Session Reminder Notification',
    description: 'Repeated reminders after session time is up'
  }
]

const notifications = reactive({
  planning_start: {
    enabled: true,
    config: {
      sound_enabled: true,
      sound_file: 'complete.oga',
      sound_repeat: 1
    }
  },
  session_end: {
    enabled: true,
    config: {
      sound_enabled: true,
      sound_file: 'complete.oga',
      sound_repeat: 1
    }
  },
  session_reminder: {
    enabled: true,
    config: {
      sound_enabled: true,
      sound_file: 'dialog-warning.oga',
      sound_repeat: 2
    }
  }
})

const availableSounds = ref([])
const loading = ref(true)
const saving = ref(false)

onMounted(async () => {
  await loadSettings()
  await loadAvailableSounds()
  loading.value = false
})

async function loadSettings() {
  const settings = await settingsStore.getAll()

  // General settings
  general.language = settings.language || 'en'
  general.notification_interval_default = settings.notification_interval_default || 10
  general.session_poll_interval = settings.session_poll_interval || 120

  // Notification settings
  for (const type of notificationTypes) {
    const enabledKey = `notification_${type.key}_enabled`
    const configKey = `notification_${type.key}_configuration`

    if (settings[enabledKey] !== undefined) {
      notifications[type.key].enabled = settings[enabledKey]
    }

    if (settings[configKey]) {
      notifications[type.key].config = settings[configKey]
    }
  }
}

async function loadAvailableSounds() {
  try {
    availableSounds.value = await settingsStore.getAvailableSounds()
  } catch (error) {
    console.error('Failed to load sounds:', error)
    availableSounds.value = ['complete.oga', 'dialog-warning.oga']
  }
}

async function saveSettings() {
  saving.value = true

  try {
    const updates = {
      // General
      language: general.language,
      notification_interval_default: general.notification_interval_default,
      session_poll_interval: general.session_poll_interval
    }

    // Notifications
    for (const type of notificationTypes) {
      updates[`notification_${type.key}_enabled`] = notifications[type.key].enabled
      updates[`notification_${type.key}_configuration`] = notifications[type.key].config
    }

    await settingsStore.updateMultiple(updates)

    alert('Settings saved successfully!')
  } catch (error) {
    console.error('Failed to save settings:', error)
    alert('Failed to save settings. Please try again.')
  } finally {
    saving.value = false
  }
}

function resetToDefaults() {
  if (!confirm('Reset all settings to defaults?')) return

  general.language = 'en'
  general.notification_interval_default = 10
  general.session_poll_interval = 120

  notificationTypes.forEach(type => {
    notifications[type.key].enabled = true
    notifications[type.key].config = {
      sound_enabled: true,
      sound_file: 'complete.oga',
      sound_repeat: 1
    }
  })
}

function previewSound(soundFile) {
  const audio = new Audio(`/sounds/${soundFile}`)
  audio.play().catch(err => {
    console.error('Failed to play sound:', err)
    alert('Failed to play sound preview')
  })
}
</script>

<template>
  <div class="settings-page">
    <div v-if="loading" class="loading">Loading settings...</div>

    <div v-else class="settings-container">
      <h1>Settings</h1>

      <!-- General Settings -->
      <section class="settings-section">
        <h2>General Settings</h2>

        <div class="setting-item">
          <label>Language</label>
          <select v-model="general.language" class="setting-input">
            <option value="en">English</option>
            <option value="fa">فارسی (Persian)</option>
          </select>
        </div>

        <div class="setting-item">
          <label>Default Reminder Interval (minutes)</label>
          <input
            v-model.number="general.notification_interval_default"
            type="number"
            min="1"
            max="120"
            class="setting-input"
          />
          <p class="setting-help">How often to remind about unstarted planned work.</p>
        </div>

        <div class="setting-item">
          <label>Session Poll Interval (seconds)</label>
          <input
            v-model.number="general.session_poll_interval"
            type="number"
            min="10"
            max="600"
            class="setting-input"
          />
          <p class="setting-help">How often to check for session updates in the web interface.</p>
        </div>
      </section>

      <!-- Notification Settings -->
      <section class="settings-section">
        <h2>Notification Settings</h2>

        <div
          v-for="type in notificationTypes"
          :key="type.key"
          class="notification-config"
        >
          <h3>{{ type.label }}</h3>
          <p class="notification-description">{{ type.description }}</p>

          <div class="setting-item">
            <label class="checkbox-label">
              <input
                v-model="notifications[type.key].enabled"
                type="checkbox"
              />
              Enable notifications
            </label>
          </div>

          <div v-if="notifications[type.key].enabled" class="sound-settings">
            <div class="setting-item">
              <label class="checkbox-label">
                <input
                  v-model="notifications[type.key].config.sound_enabled"
                  type="checkbox"
                />
                Play sound
              </label>
            </div>

            <div v-if="notifications[type.key].config.sound_enabled" class="sound-config">
              <div class="setting-item">
                <label>Sound File</label>
                <div class="sound-select-row">
                  <select
                    v-model="notifications[type.key].config.sound_file"
                    class="setting-input"
                  >
                    <option
                      v-for="sound in availableSounds"
                      :key="sound"
                      :value="sound"
                    >
                      {{ sound }}
                    </option>
                  </select>
                  <button
                    @click="previewSound(notifications[type.key].config.sound_file)"
                    class="btn-preview"
                  >
                    ▶ Preview
                  </button>
                </div>
              </div>

              <div class="setting-item">
                <label>Play Count</label>
                <select
                  v-model.number="notifications[type.key].config.sound_repeat"
                  class="setting-input"
                >
                  <option :value="1">1 time</option>
                  <option :value="2">2 times</option>
                  <option :value="3">3 times</option>
                  <option :value="4">4 times</option>
                  <option :value="5">5 times</option>
                </select>
              </div>
            </div>
          </div>
        </div>
      </section>

      <!-- Actions -->
      <div class="actions">
        <button @click="resetToDefaults" class="btn btn-secondary">
          Reset to Defaults
        </button>
        <button @click="saveSettings" :disabled="saving" class="btn btn-primary">
          {{ saving ? 'Saving...' : 'Save Changes' }}
        </button>
      </div>
    </div>
  </div>
</template>

<style scoped>
.settings-page {
  max-width: 900px;
  margin: 2rem auto;
  padding: 0 1rem;
}

.settings-container {
  background: white;
  border-radius: 0.5rem;
  padding: 2rem;
  box-shadow: 0 1px 3px rgba(0,0,0,0.1);
}

h1 {
  font-size: 1.875rem;
  font-weight: 700;
  margin-bottom: 2rem;
}

.settings-section {
  margin-bottom: 3rem;
}

.settings-section h2 {
  font-size: 1.5rem;
  font-weight: 600;
  margin-bottom: 1.5rem;
  padding-bottom: 0.5rem;
  border-bottom: 2px solid #e5e7eb;
}

.notification-config {
  background: #f9fafb;
  border-radius: 0.5rem;
  padding: 1.5rem;
  margin-bottom: 1.5rem;
}

.notification-config h3 {
  font-size: 1.125rem;
  font-weight: 600;
  margin-bottom: 0.5rem;
}

.notification-description {
  color: #6b7280;
  margin-bottom: 1rem;
  font-size: 0.875rem;
}

.setting-item {
  margin-bottom: 1.5rem;
}

.setting-item label {
  display: block;
  font-weight: 500;
  margin-bottom: 0.5rem;
  color: #374151;
}

.setting-input {
  width: 100%;
  max-width: 400px;
  padding: 0.5rem 0.75rem;
  border: 1px solid #d1d5db;
  border-radius: 0.375rem;
  font-size: 1rem;
}

.setting-input:focus {
  outline: none;
  border-color: #3b82f6;
  ring: 2px;
  ring-color: #3b82f6;
  ring-opacity: 0.5;
}

.setting-help {
  margin-top: 0.5rem;
  font-size: 0.875rem;
  color: #6b7280;
}

.checkbox-label {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  cursor: pointer;
}

.checkbox-label input[type="checkbox"] {
  width: 1.125rem;
  height: 1.125rem;
  cursor: pointer;
}

.sound-settings {
  margin-left: 2rem;
  margin-top: 1rem;
}

.sound-config {
  margin-left: 2rem;
  margin-top: 1rem;
}

.sound-select-row {
  display: flex;
  gap: 0.5rem;
  align-items: center;
}

.btn-preview {
  padding: 0.5rem 1rem;
  background: #3b82f6;
  color: white;
  border: none;
  border-radius: 0.375rem;
  cursor: pointer;
  white-space: nowrap;
}

.btn-preview:hover {
  background: #2563eb;
}

.actions {
  display: flex;
  gap: 1rem;
  justify-content: flex-end;
  margin-top: 2rem;
  padding-top: 2rem;
  border-top: 1px solid #e5e7eb;
}

.btn {
  padding: 0.625rem 1.25rem;
  border-radius: 0.375rem;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.2s;
}

.btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.btn-secondary {
  background: white;
  border: 1px solid #d1d5db;
  color: #374151;
}

.btn-secondary:hover:not(:disabled) {
  background: #f9fafb;
}

.btn-primary {
  background: #3b82f6;
  border: 1px solid #3b82f6;
  color: white;
}

.btn-primary:hover:not(:disabled) {
  background: #2563eb;
}

.loading {
  text-align: center;
  padding: 3rem;
  color: #6b7280;
}
</style>
```

### Backend API

Create `backend/app/api/settings.py`:

```python
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import Dict, Any, List
from app.core.database import get_db
from app.models.setting import Setting
from pydantic import BaseModel
import json

router = APIRouter(prefix="/api/settings", tags=["settings"])

class SettingUpdate(BaseModel):
    key_name: str
    value: Any

class BulkSettingUpdate(BaseModel):
    settings: Dict[str, Any]

@router.get("/")
async def get_all_settings(db: Session = Depends(get_db)) -> Dict[str, Any]:
    """Get all settings as a dictionary."""
    settings = db.query(Setting).all()

    result = {}
    for setting in settings:
        # Parse JSON value
        try:
            result[setting.key_name] = json.loads(setting.value_json)
        except:
            result[setting.key_name] = setting.value_json

    return result

@router.get("/{key_name}")
async def get_setting(key_name: str, db: Session = Depends(get_db)):
    """Get a specific setting."""
    setting = db.query(Setting).filter(Setting.key_name == key_name).first()

    if not setting:
        raise HTTPException(status_code=404, detail="Setting not found")

    try:
        return json.loads(setting.value_json)
    except:
        return setting.value_json

@router.put("/{key_name}")
async def update_setting(
    key_name: str,
    value: Any,
    db: Session = Depends(get_db)
):
    """Update a setting value."""
    setting = db.query(Setting).filter(Setting.key_name == key_name).first()

    value_json = json.dumps(value)

    if setting:
        setting.value_json = value_json
    else:
        setting = Setting(key_name=key_name, value_json=value_json)
        db.add(setting)

    db.commit()
    db.refresh(setting)

    return {"key_name": key_name, "value": value}

@router.post("/bulk-update")
async def bulk_update_settings(
    updates: BulkSettingUpdate,
    db: Session = Depends(get_db)
):
    """Update multiple settings at once."""
    for key_name, value in updates.settings.items():
        setting = db.query(Setting).filter(Setting.key_name == key_name).first()

        value_json = json.dumps(value)

        if setting:
            setting.value_json = value_json
        else:
            setting = Setting(key_name=key_name, value_json=value_json)
            db.add(setting)

    db.commit()

    return {"updated": len(updates.settings)}

@router.get("/sounds/available")
async def get_available_sounds() -> List[str]:
    """Get list of available sound files."""
    import os
    from pathlib import Path

    sounds = []

    # System sounds
    system_sounds_dir = Path("/usr/share/sounds/freedesktop/stereo")
    if system_sounds_dir.exists():
        sounds.extend([f.name for f in system_sounds_dir.glob("*.oga")])

    # Custom sounds
    custom_sounds_dir = Path(__file__).parent.parent.parent / "sounds"
    if custom_sounds_dir.exists():
        sounds.extend([f.name for f in custom_sounds_dir.glob("*.*")])

    return sorted(set(sounds))
```

### Pinia Store

Create `frontend/src/stores/settings.js`:

```javascript
import { defineStore } from 'pinia'
import api from '@/services/api'

export const useSettingsStore = defineStore('settings', {
  state: () => ({
    settings: {}
  }),

  actions: {
    async getAll() {
      const response = await api.get('/api/settings')
      this.settings = response.data
      return this.settings
    },

    async get(key) {
      const response = await api.get(`/api/settings/${key}`)
      return response.data
    },

    async update(key, value) {
      const response = await api.put(`/api/settings/${key}`, value)
      this.settings[key] = value
      return response.data
    },

    async updateMultiple(updates) {
      const response = await api.post('/api/settings/bulk-update', {
        settings: updates
      })
      Object.assign(this.settings, updates)
      return response.data
    },

    async getAvailableSounds() {
      const response = await api.get('/api/settings/sounds/available')
      return response.data
    }
  }
})
```

## Checklist

- [ ] Settings page created
- [ ] All general settings editable
- [ ] Notification settings for all 3 types
- [ ] Sound preview works
- [ ] Backend API endpoints created
- [ ] Settings store created
- [ ] Bulk update works
- [ ] Reset to defaults works
- [ ] Changes persist after save
- [ ] Available sounds loaded
- [ ] Validation on numeric inputs
- [ ] Navigation item added to menu

## Notes

- Settings take effect immediately after save
- Notification worker reads settings on each check
- Sound files served from `/sounds/` endpoint
- System sounds referenced from system directory
