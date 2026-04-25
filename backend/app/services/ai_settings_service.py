"""Persistent AI configuration.

Stored as a single JSON blob in the existing ``settings`` key/value table
under the key ``ai.config``. Falls back to defaults derived from environment
variables (loaded by :mod:`app.core.config`) when no row exists yet.
"""
from __future__ import annotations

from typing import Any, Dict, Optional

from sqlalchemy.orm import Session

from app.core.config import settings as env_settings
from app.services.setting_service import SettingService


SETTINGS_KEY = "ai.config"

DEFAULT_SYSTEM_PROMPT = (
    "You are the user's planning + journaling assistant inside Ubuntu-Planner. "
    "You help with day-memory journaling, planning slots, work sessions, "
    "and you keep your own observations in a separate AI track. "
    "Use the available tools whenever a question requires real data. "
    "Be concise and direct. Confirm before doing anything destructive."
)


def _default_config() -> Dict[str, Any]:
    return {
        "enabled": getattr(env_settings, "AI_ENABLED", False),
        "provider": getattr(env_settings, "AI_PROVIDER", "openai_compatible"),
        "model": getattr(env_settings, "AI_MODEL", "openai/gpt-oss-120b:free"),
        "base_url": getattr(env_settings, "AI_BASE_URL", "https://openrouter.ai/api/v1"),
        "api_key": getattr(env_settings, "AI_API_KEY", "") or "",
        "system_prompt": DEFAULT_SYSTEM_PROMPT,
        "user_prompt": "",
        "permissions": {},
        "max_tool_iterations": 10,
        "request_timeout": 120,
    }


class AISettingsService:
    def __init__(self, db: Session) -> None:
        self.db = db
        self._settings = SettingService(db)

    def get_config(self) -> Dict[str, Any]:
        stored = self._settings.get_by_key(SETTINGS_KEY) or {}
        merged = _default_config()
        if isinstance(stored, dict):
            merged.update({k: v for k, v in stored.items() if v is not None})
        return merged

    def update_config(self, patch: Dict[str, Any]) -> Dict[str, Any]:
        config = self.get_config()
        for key in (
            "enabled",
            "provider",
            "model",
            "base_url",
            "api_key",
            "system_prompt",
            "user_prompt",
            "permissions",
            "max_tool_iterations",
            "request_timeout",
        ):
            if key in patch and patch[key] is not None:
                config[key] = patch[key]
        # Persist as single dict so future fields don't need a migration.
        self._settings.set(SETTINGS_KEY, config)
        return config

    def is_enabled(self) -> bool:
        return bool(self.get_config().get("enabled"))
