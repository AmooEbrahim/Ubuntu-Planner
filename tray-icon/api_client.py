"""API client for Ubuntu Planner backend."""
import requests
from typing import Optional, Dict, List
from config import config


class APIClient:
    """Client for Ubuntu Planner backend API."""

    def __init__(self):
        """Initialize API client."""
        self.base_url = config.API_BASE_URL
        self.session = requests.Session()
        self.session.timeout = 5

    def get_active_session(self) -> Optional[Dict]:
        """Get currently active session.

        Returns:
            Active session data or None
        """
        try:
            response = self.session.get(f"{self.base_url}/api/sessions/active")
            return response.json() if response.status_code == 200 else None
        except Exception as e:
            print(f"Failed to get active session: {e}")
            return None

    def get_current_planning(self) -> Optional[Dict]:
        """Get planning for current time window.

        Returns:
            Current planning data or None
        """
        try:
            response = self.session.get(f"{self.base_url}/api/planning/current")
            return response.json() if response.status_code == 200 else None
        except Exception as e:
            print(f"Failed to get current planning: {e}")
            return None

    def get_pinned_projects(self) -> List[Dict]:
        """Get pinned projects.

        Returns:
            List of pinned projects
        """
        try:
            response = self.session.get(f"{self.base_url}/api/projects/pinned")
            return response.json() if response.status_code == 200 else []
        except Exception as e:
            print(f"Failed to get pinned projects: {e}")
            return []

    def get_recent_projects(self, limit: int = 3) -> List[Dict]:
        """Get recent projects from sessions.

        Args:
            limit: Maximum number of projects to return

        Returns:
            List of recent projects
        """
        try:
            response = self.session.get(f"{self.base_url}/api/projects/recent?limit={limit}")
            return response.json() if response.status_code == 200 else []
        except Exception as e:
            print(f"Failed to get recent projects: {e}")
            return []

    def start_session(self, project_id: Optional[int], planned_duration: int) -> Dict:
        """Start a new session.

        Args:
            project_id: ID of project (None for projectless session)
            planned_duration: Planned duration in minutes

        Returns:
            Created session data

        Raises:
            Exception: If request fails
        """
        data = {
            "project_id": project_id,
            "planned_duration": planned_duration
        }
        response = self.session.post(f"{self.base_url}/api/sessions/", json=data)
        response.raise_for_status()
        return response.json()

    def stop_session_quick(self, session_id: int) -> Dict:
        """Stop session without review.

        Args:
            session_id: ID of session to stop

        Returns:
            Updated session data

        Raises:
            Exception: If request fails
        """
        response = self.session.post(f"{self.base_url}/api/sessions/{session_id}/stop")
        response.raise_for_status()
        return response.json()

    def toggle_notifications(self, session_id: int) -> Dict:
        """Toggle notifications for session.

        Args:
            session_id: ID of session

        Returns:
            Updated session data

        Raises:
            Exception: If request fails
        """
        response = self.session.post(f"{self.base_url}/api/sessions/{session_id}/toggle-notifications")
        response.raise_for_status()
        return response.json()


# Global instance
api = APIClient()
