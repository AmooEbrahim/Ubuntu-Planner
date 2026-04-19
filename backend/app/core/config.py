from pydantic_settings import BaseSettings, SettingsConfigDict
from pathlib import Path
from typing import Optional


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    DB_CONNECTION: str = "MySQL"
    DB_HOST: str
    DB_USERNAME: str
    DB_PASSWORD: str
    DB_DATABASE: str

    NOTIFICATION_HOST: str
    NOTIFICATION_PORT: int

    API_HOST: str = "localhost"
    API_PORT: int = 9090
    FRONTEND_PORT: int = 5173
    DEBUG: bool = False

    NOTIFICATION_CONFIG_DIR: Optional[str] = None
    SOUNDS_DIR: Optional[str] = None

    model_config = SettingsConfigDict(
        env_file=Path(__file__).resolve().parent.parent.parent.parent / ".env",
        extra="ignore",
    )

    @property
    def database_url(self) -> str:
        """Generate SQLAlchemy database URL."""
        return f"mysql+pymysql://{self.DB_USERNAME}:{self.DB_PASSWORD}@{self.DB_HOST}/{self.DB_DATABASE}"

    @property
    def notification_config_dir(self) -> Path:
        """Get notification config directory path."""
        if self.NOTIFICATION_CONFIG_DIR:
            return Path(self.NOTIFICATION_CONFIG_DIR)
        return Path.home() / "bin/bash/Ubuntu-Planner/notifications"

    @property
    def sounds_dir(self) -> Path:
        """Get sounds directory path."""
        if self.SOUNDS_DIR:
            return Path(self.SOUNDS_DIR)
        return Path(__file__).parent.parent.parent.parent / "sounds"


settings = Settings()
