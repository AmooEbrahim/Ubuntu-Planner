from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import Optional
from pathlib import Path


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    # Database
    DB_CONNECTION: str = "MySQL"
    DB_HOST: str
    DB_USERNAME: str
    DB_PASSWORD: str
    DB_DATABASE: str

    # Notification
    NOTIFICATION_HOST: str
    NOTIFICATION_PORT: int

    # Application
    API_HOST: str = "localhost"
    API_PORT: int = 9090
    FRONTEND_PORT: int = 5173
    DEBUG: bool = False

    model_config = SettingsConfigDict(
        env_file=Path(__file__).resolve().parent.parent.parent.parent / ".env",
        extra="ignore",
    )

    @property
    def database_url(self) -> str:
        """Generate SQLAlchemy database URL."""
        return f"mysql+pymysql://{self.DB_USERNAME}:{self.DB_PASSWORD}@{self.DB_HOST}/{self.DB_DATABASE}"


settings = Settings()
