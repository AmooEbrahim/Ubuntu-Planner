# Phase 5: System Tray Integration & Settings

Desktop integration with system tray icon, session review workflow, and comprehensive settings management.

## Objectives

- Create system tray icon application for quick access
- Implement session review page with detailed feedback
- Build settings management interface
- Enhance notification system with configurable sounds
- Integrate all components with existing system

## Features

### 1. System Tray Icon
- Desktop tray icon using GTK AppIndicator3
- Quick session start/stop controls
- Show current session status
- Access to pinned and recent projects
- Communication with backend API

### 2. Session Review Page
- Detailed session completion workflow
- Satisfaction rating (0-100)
- Tasks completed tracking
- Personal notes
- Redirect to sessions list after save

### 3. Settings Management
- General settings editor
- Notification configuration per type
- Sound selection and management
- Default interval customization

### 4. Sound System
- Centralized sound file storage
- System sounds integration (/usr/share/sounds/)
- Custom sound upload support
- Per-notification-type configuration

## Components

| Component | Type | Description |
|-----------|------|-------------|
| Tray Icon App | Python/GTK | Desktop tray application |
| Session Review Page | Vue 3 | Detailed session feedback form |
| Settings Page | Vue 3 | Settings management interface |
| Settings API | FastAPI | Backend for settings CRUD |
| Sound Manager | Python | Sound file management service |
| Notification Enhancer | Python | Apply sound settings to notifications |

## Database Changes

### Settings Table (existing)
Add new settings:
- `notification_planning_start_enabled`
- `notification_planning_start_configuration`
- `notification_session_end_enabled`
- `notification_session_end_configuration`
- `notification_session_reminder_enabled`
- `notification_session_reminder_configuration`

### Sessions Table
No changes required (already has satisfaction, tasks, notes fields)

## Architecture

```
┌─────────────────┐
│  System Tray    │◄─────┐
│   (GTK/Python)  │      │
└────────┬────────┘      │
         │               │
         │ HTTP API      │
         │               │
┌────────▼────────┐      │
│   Backend API   │      │
│   (Port 1717)   │      │
└────────┬────────┘      │
         │               │
         │ Websocket     │
         │ (Optional)    │
┌────────▼────────┐      │
│   Frontend      │──────┘
│   (Port 1718)   │
└─────────────────┘
```

## Implementation Order

1. **Tray Icon Foundation** → Create basic GTK tray app
2. **Backend Settings API** → CRUD endpoints for settings
3. **Settings Page** → Frontend settings management
4. **Sound Management** → Sound file system and selection
5. **Session Review Page** → Detailed feedback form
6. **Tray Integration** → Connect all components
7. **Notification Enhancement** → Apply sound settings

## Development Workflow

- Update `start-dev.sh` to launch tray icon
- Tray icon runs alongside backend and frontend
- All three components communicate via API

## Testing Checklist

- [ ] Tray icon appears in system tray
- [ ] Tray menu shows correct options based on session state
- [ ] Can start session from tray
- [ ] Can stop session from tray (quick and full)
- [ ] Full stop opens review page in browser
- [ ] Review page saves data correctly
- [ ] Settings page loads and saves
- [ ] Sound preview works in settings
- [ ] Notifications use configured sounds
- [ ] All three notification types configurable separately

## Files to Create/Modify

### New Files
- `tray-icon/main.py` - Tray application entry
- `tray-icon/indicator.py` - GTK indicator logic
- `tray-icon/api_client.py` - Backend API client
- `tray-icon/requirements.txt` - Python dependencies
- `backend/app/api/settings.py` - Settings API routes
- `backend/app/services/settings_service.py` - Settings logic
- `frontend/src/views/SessionReview.vue` - Review page
- `frontend/src/views/Settings.vue` - Settings page
- `sounds/README.md` - Sound files documentation

### Modified Files
- `backend/app/services/notification_service.py` - Add sound support
- `backend/app/tasks/notification_worker.py` - Use settings
- `start-dev.sh` - Add tray icon startup
- `Documents/readme-execution.md` - Document tray icon
- `Documents/readme-web-interface.md` - Add new pages

## Dependencies

### Backend
No new dependencies (existing SQLAlchemy for settings)

### Frontend
No new dependencies (existing Pinia, Vue Router)

### Tray Icon
```txt
PyGObject==3.42.0
pycairo==1.21.0
requests==2.31.0
python-dotenv==1.0.0
```

## Next Steps

After Phase 5:
- Analytics and reporting (Phase 6)
- Data export/import (Phase 7)
- Multi-user support (Phase 8)

## Notes

- Tray icon is optional; web interface remains fully functional
- Settings changes apply immediately to running sessions
- Sound files stored in `sounds/` directory
- System sounds referenced from `/usr/share/sounds/freedesktop/stereo/`
