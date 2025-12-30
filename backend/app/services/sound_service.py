"""Sound file management service."""
from pathlib import Path
from typing import List, Optional
import os


class SoundService:
    """Service for managing sound files."""

    def __init__(self):
        """Initialize sound service."""
        self.project_root = Path(__file__).parent.parent.parent.parent
        self.custom_sounds_dir = self.project_root / "sounds"
        self.system_sounds_dir = Path("/usr/share/sounds/freedesktop/stereo")

        # Ensure custom sounds directory exists
        self.custom_sounds_dir.mkdir(exist_ok=True)

    def get_available_sounds(self) -> List[str]:
        """Get list of all available sound files.

        Returns:
            List of sound file names
        """
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
        """Get full path to a sound file.

        Args:
            filename: Name of the sound file

        Returns:
            Path to sound file, or None if not found
        """
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
        """Check if sound file exists.

        Args:
            filename: Name of the sound file

        Returns:
            True if file exists, False otherwise
        """
        return self.get_sound_path(filename) is not None

    def get_default_sounds(self) -> dict:
        """Get default sound configuration.

        Returns:
            Dictionary of default sounds for each notification type
        """
        return {
            "planning_start": "complete.oga",
            "session_end": "complete.oga",
            "session_reminder": "dialog-warning.oga"
        }


# Global instance
sound_service = SoundService()
