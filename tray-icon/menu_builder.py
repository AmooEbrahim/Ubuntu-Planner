"""Dynamic menu builder for tray icon."""
import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk
from typing import Optional, Dict, List


class MenuBuilder:
    """Build dynamic menu based on session state."""

    def __init__(self, api_client, on_start_session, on_stop_quick, on_stop_full, on_toggle_notif):
        """Initialize menu builder.

        Args:
            api_client: API client instance
            on_start_session: Callback for starting session
            on_stop_quick: Callback for quick stop
            on_stop_full: Callback for stop with review
            on_toggle_notif: Callback for toggling notifications
        """
        self.api = api_client
        self.on_start_session = on_start_session
        self.on_stop_quick = on_stop_quick
        self.on_stop_full = on_stop_full
        self.on_toggle_notif = on_toggle_notif

    def build(self) -> Gtk.Menu:
        """Build menu based on current state.

        Returns:
            GTK menu
        """
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
        """Build menu when no active session.

        Args:
            menu: GTK menu to populate
        """
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
        """Build menu when session is active.

        Args:
            menu: GTK menu to populate
            session: Active session data
        """
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
