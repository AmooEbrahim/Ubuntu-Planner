"""System tray indicator for Ubuntu Planner."""
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
        """Initialize planner indicator."""
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
        """Periodically update menu and icon.

        Returns:
            True to continue polling
        """
        self.update_menu()
        return True  # Continue polling

    def on_start_session(self, project_id, duration):
        """Start a new session.

        Args:
            project_id: Project ID or None
            duration: Planned duration in minutes
        """
        try:
            api.start_session(project_id, duration)
            self.update_menu()
        except Exception as e:
            self.show_error(f"Failed to start session: {e}")

    def on_stop_quick(self, session_id):
        """Stop session without review.

        Args:
            session_id: Session ID to stop
        """
        try:
            api.stop_session_quick(session_id)
            self.update_menu()
        except Exception as e:
            self.show_error(f"Failed to stop session: {e}")

    def on_stop_full(self, session_id):
        """Stop session and open review page.

        Args:
            session_id: Session ID to stop
        """
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
        """Toggle notifications for session.

        Args:
            session_id: Session ID
        """
        try:
            api.toggle_notifications(session_id)
            self.update_menu()
        except Exception as e:
            self.show_error(f"Failed to toggle notifications: {e}")

    def show_error(self, message):
        """Show error notification.

        Args:
            message: Error message to display
        """
        dialog = Gtk.MessageDialog(
            message_type=Gtk.MessageType.ERROR,
            buttons=Gtk.ButtonsType.OK,
            text=message
        )
        dialog.run()
        dialog.destroy()
