# System Tray Icon Application

GTK-based system tray application for quick access to Ubuntu Planner.

## Overview

Desktop tray icon that:
- Shows session status at a glance
- Provides quick session controls
- Integrates with Ubuntu system tray
- Communicates with backend API (port 1717)

## Technology Stack

- **Python 3.10+**
- **GTK 3** with PyGObject
- **AppIndicator3** for system tray
- **Requests** for API communication

## Project Structure

```
tray-icon/
├── main.py                # Entry point
├── indicator.py           # GTK indicator logic
├── api_client.py          # Backend API client
├── menu_builder.py        # Dynamic menu construction
├── config.py              # Configuration loader
├── requirements.txt       # Dependencies
└── assets/
    ├── icon-idle.png      # Icon when no session
    ├── icon-active.png    # Icon when session active
    └── icon-overtime.png  # Icon when overtime
```

## Implementation

### 1. Dependencies (requirements.txt)

```txt
PyGObject==3.42.0
pycairo==1.21.0
requests==2.31.0
python-dotenv==1.0.0
```

### 2. Configuration (config.py)

```python
import os
from pathlib import Path
from dotenv import load_dotenv

# Load .env from project root
project_root = Path(__file__).parent.parent
load_dotenv(project_root / '.env')

class Config:
    API_BASE_URL = f"http://{os.getenv('API_HOST', 'localhost')}:{os.getenv('API_PORT', '1717')}"
    FRONTEND_URL = f"http://localhost:{os.getenv('FRONTEND_PORT', '1718')}"
    POLL_INTERVAL = 30  # seconds
    ASSETS_DIR = Path(__file__).parent / 'assets'

config = Config()
```

### 3. API Client (api_client.py)

```python
import requests
from typing import Optional, Dict, List
from config import config

class APIClient:
    """Client for Ubuntu Planner backend API."""

    def __init__(self):
        self.base_url = config.API_BASE_URL
        self.session = requests.Session()
        self.session.timeout = 5

    def get_active_session(self) -> Optional[Dict]:
        """Get currently active session."""
        try:
            response = self.session.get(f"{self.base_url}/api/sessions/active")
            return response.json() if response.status_code == 200 else None
        except:
            return None

    def get_current_planning(self) -> Optional[Dict]:
        """Get planning for current time window."""
        try:
            response = self.session.get(f"{self.base_url}/api/planning/current")
            return response.json() if response.status_code == 200 else None
        except:
            return None

    def get_pinned_projects(self) -> List[Dict]:
        """Get pinned projects."""
        try:
            response = self.session.get(f"{self.base_url}/api/projects?pinned=true")
            return response.json() if response.status_code == 200 else []
        except:
            return []

    def get_recent_projects(self, limit: int = 3) -> List[Dict]:
        """Get recent projects from sessions."""
        try:
            response = self.session.get(f"{self.base_url}/api/projects/recent?limit={limit}")
            return response.json() if response.status_code == 200 else []
        except:
            return []

    def start_session(self, project_id: Optional[int], planned_duration: int) -> Dict:
        """Start a new session."""
        data = {
            "project_id": project_id,
            "planned_duration": planned_duration
        }
        response = self.session.post(f"{self.base_url}/api/sessions/start", json=data)
        response.raise_for_status()
        return response.json()

    def stop_session_quick(self, session_id: int) -> Dict:
        """Stop session without review."""
        response = self.session.post(f"{self.base_url}/api/sessions/{session_id}/stop")
        response.raise_for_status()
        return response.json()

    def toggle_notifications(self, session_id: int) -> Dict:
        """Toggle notifications for session."""
        response = self.session.post(f"{self.base_url}/api/sessions/{session_id}/toggle-notifications")
        response.raise_for_status()
        return response.json()

api = APIClient()
```

### 4. Menu Builder (menu_builder.py)

```python
import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk
from typing import Optional, Dict, List

class MenuBuilder:
    """Build dynamic menu based on session state."""

    def __init__(self, api_client, on_start_session, on_stop_quick, on_stop_full, on_toggle_notif):
        self.api = api_client
        self.on_start_session = on_start_session
        self.on_stop_quick = on_stop_quick
        self.on_stop_full = on_stop_full
        self.on_toggle_notif = on_toggle_notif

    def build(self) -> Gtk.Menu:
        """Build menu based on current state."""
        menu = Gtk.Menu()

        # Get current state
        active_session = self.api.get_active_session()

        if active_session:
            self._build_active_menu(menu, active_session)
        else:
            self._build_idle_menu(menu)

        # Always add separator and quit
        menu.append(Gtk.SeparatorMenuItem())

        item_open = Gtk.MenuItem(label="Open Web Interface")
        item_open.connect('activate', self._open_web)
        menu.append(item_open)

        item_quit = Gtk.MenuItem(label="Quit")
        item_quit.connect('activate', Gtk.main_quit)
        menu.append(item_quit)

        menu.show_all()
        return menu

    def _build_idle_menu(self, menu: Gtk.Menu):
        """Build menu when no active session."""
        # Current planning
        planning = self.api.get_current_planning()
        if planning:
            label = f"▶ Start: {planning['project']['name']} ({planning['planned_duration']}m)"
            item = Gtk.MenuItem(label=label)
            item.connect('activate', lambda _: self.on_start_session(planning['project']['id'], planning['planned_duration']))
            menu.append(item)
            menu.append(Gtk.SeparatorMenuItem())

        # Start without project
        item = Gtk.MenuItem(label="Start Session (No Project)")
        item.connect('activate', lambda _: self.on_start_session(None, 60))
        menu.append(item)

        # Pinned projects
        pinned = self.api.get_pinned_projects()
        if pinned:
            menu.append(Gtk.SeparatorMenuItem())
            pinned_label = Gtk.MenuItem(label="Pinned Projects")
            pinned_label.set_sensitive(False)
            menu.append(pinned_label)

            for project in pinned[:5]:
                item = Gtk.MenuItem(label=f"  {project['name']} ({project['default_duration']}m)")
                item.connect('activate', lambda _, p=project: self.on_start_session(p['id'], p['default_duration']))
                menu.append(item)

        # Recent projects
        recent = self.api.get_recent_projects(3)
        if recent:
            menu.append(Gtk.SeparatorMenuItem())
            recent_label = Gtk.MenuItem(label="Recent Projects")
            recent_label.set_sensitive(False)
            menu.append(recent_label)

            for project in recent:
                item = Gtk.MenuItem(label=f"  {project['name']} ({project['default_duration']}m)")
                item.connect('activate', lambda _, p=project: self.on_start_session(p['id'], p['default_duration']))
                menu.append(item)

    def _build_active_menu(self, menu: Gtk.Menu, session: Dict):
        """Build menu when session is active."""
        project_name = session['project']['name'] if session.get('project') else 'No Project'
        elapsed = session.get('elapsed_minutes', 0)
        planned = session['planned_duration']

        # Session info (non-clickable)
        info_label = f"🟢 {project_name}"
        item_info = Gtk.MenuItem(label=info_label)
        item_info.set_sensitive(False)
        menu.append(item_info)

        time_label = f"   {elapsed}m / {planned}m"
        item_time = Gtk.MenuItem(label=time_label)
        item_time.set_sensitive(False)
        menu.append(item_time)

        menu.append(Gtk.SeparatorMenuItem())

        # Stop options
        item_stop_full = Gtk.MenuItem(label="Stop & Review")
        item_stop_full.connect('activate', lambda _: self.on_stop_full(session['id']))
        menu.append(item_stop_full)

        item_stop_quick = Gtk.MenuItem(label="Quick Stop")
        item_stop_quick.connect('activate', lambda _: self.on_stop_quick(session['id']))
        menu.append(item_stop_quick)

        menu.append(Gtk.SeparatorMenuItem())

        # Toggle notifications
        notif_label = "🔕 Disable Notifications" if not session.get('notification_disabled') else "🔔 Enable Notifications"
        item_notif = Gtk.MenuItem(label=notif_label)
        item_notif.connect('activate', lambda _: self.on_toggle_notif(session['id']))
        menu.append(item_notif)

    def _open_web(self, _):
        """Open web interface in browser."""
        import webbrowser
        from config import config
        webbrowser.open(config.FRONTEND_URL)

```

### 5. Indicator Logic (indicator.py)

```python
import gi
gi.require_version('Gtk', '3.0')
gi.require_version('AppIndicator3', '0.1')
from gi.repository import Gtk, AppIndicator3, GLib
import webbrowser
from config import config
from api_client import api
from menu_builder import MenuBuilder

class PlannerIndicator:
    """System tray indicator for Ubuntu Planner."""

    def __init__(self):
        self.indicator = AppIndicator3.Indicator.new(
            "ubuntu-planner",
            str(config.ASSETS_DIR / "icon-idle.png"),
            AppIndicator3.IndicatorCategory.APPLICATION_STATUS
        )
        self.indicator.set_status(AppIndicator3.IndicatorStatus.ACTIVE)

        # Menu builder
        self.menu_builder = MenuBuilder(
            api,
            self.on_start_session,
            self.on_stop_quick,
            self.on_stop_full,
            self.on_toggle_notifications
        )

        # Build initial menu
        self.update_menu()

        # Poll for updates
        GLib.timeout_add_seconds(config.POLL_INTERVAL, self.poll_update)

    def update_menu(self):
        """Rebuild menu based on current state."""
        menu = self.menu_builder.build()
        self.indicator.set_menu(menu)
        self.update_icon()

    def update_icon(self):
        """Update icon based on session state."""
        session = api.get_active_session()

        if not session:
            icon = "icon-idle.png"
        elif session.get('elapsed_minutes', 0) > session['planned_duration']:
            icon = "icon-overtime.png"
        else:
            icon = "icon-active.png"

        self.indicator.set_icon(str(config.ASSETS_DIR / icon))

    def poll_update(self):
        """Periodically update menu and icon."""
        self.update_menu()
        return True  # Continue polling

    def on_start_session(self, project_id, duration):
        """Start a new session."""
        try:
            api.start_session(project_id, duration)
            self.update_menu()
        except Exception as e:
            self.show_error(f"Failed to start session: {e}")

    def on_stop_quick(self, session_id):
        """Stop session without review."""
        try:
            api.stop_session_quick(session_id)
            self.update_menu()
        except Exception as e:
            self.show_error(f"Failed to stop session: {e}")

    def on_stop_full(self, session_id):
        """Stop session and open review page."""
        try:
            # Stop session first
            api.stop_session_quick(session_id)

            # Open review page in browser
            review_url = f"{config.FRONTEND_URL}/session-review/{session_id}"
            webbrowser.open(review_url)

            self.update_menu()
        except Exception as e:
            self.show_error(f"Failed to stop session: {e}")

    def on_toggle_notifications(self, session_id):
        """Toggle notifications for session."""
        try:
            api.toggle_notifications(session_id)
            self.update_menu()
        except Exception as e:
            self.show_error(f"Failed to toggle notifications: {e}")

    def show_error(self, message):
        """Show error notification."""
        dialog = Gtk.MessageDialog(
            message_type=Gtk.MessageType.ERROR,
            buttons=Gtk.ButtonsType.OK,
            text=message
        )
        dialog.run()
        dialog.destroy()
```

### 6. Main Entry Point (main.py)

```python
#!/usr/bin/env python3
import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk
from indicator import PlannerIndicator

def main():
    """Start the tray icon application."""
    indicator = PlannerIndicator()
    Gtk.main()

if __name__ == '__main__':
    main()
```

## Installation

### System Dependencies

```bash
sudo apt install python3-gi python3-gi-cairo gir1.2-gtk-3.0 gir1.2-appindicator3-0.1
```

### Python Dependencies

```bash
cd tray-icon
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

## Running

### Development

```bash
cd tray-icon
source venv/bin/activate
python3 main.py
```

### With start-dev.sh

The tray icon will be automatically started when using `start-dev.sh`.

## Icons

Create three icons in `tray-icon/assets/`:

- **icon-idle.png** - Gray/inactive (no session)
- **icon-active.png** - Green/blue (session running)
- **icon-overtime.png** - Orange/red (session overtime)

Size: 22x22 pixels (standard tray icon size)

## Checklist

- [ ] Dependencies installed
- [ ] Configuration loaded from .env
- [ ] API client connects to backend
- [ ] Tray icon appears
- [ ] Menu shows when clicked
- [ ] Idle menu shows correct options
- [ ] Can start session from menu
- [ ] Active menu shows session info
- [ ] Quick stop works
- [ ] Full stop opens review page in browser
- [ ] Toggle notifications works
- [ ] Icon changes based on state
- [ ] Periodic polling updates menu
- [ ] Open web interface works
- [ ] Error handling shows dialogs

## Notes

- Tray icon must run while backend and frontend are running
- Requires X11 or Wayland with XWayland
- AppIndicator3 is standard on Ubuntu/GNOME
- For other desktop environments, may need different approach
