"""Configuration for tray icon application."""
import os
from pathlib import Path
from dotenv import load_dotenv

# Load .env from project root
project_root = Path(__file__).parent.parent
load_dotenv(project_root / '.env')


class Config:
    """Configuration settings."""

    API_HOST = os.getenv('API_HOST', 'localhost')
    API_PORT = os.getenv('API_PORT', '1717')
    API_BASE_URL = f"http://{API_HOST}:{API_PORT}"
    FRONTEND_PORT = os.getenv('FRONTEND_PORT', '1718')
    FRONTEND_URL = f"http://localhost:{FRONTEND_PORT}"
    POLL_INTERVAL = 30  # seconds
    ASSETS_DIR = Path(__file__).parent / 'assets'


config = Config()
