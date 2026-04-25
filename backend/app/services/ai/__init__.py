"""AI subsystem.

Exposes a ``get_provider()`` factory that reads the active AI configuration
(loaded from the ``settings`` table, falling back to env-derived defaults) and
returns an instantiated :class:`~app.services.ai.provider.AIProvider`.
"""
from __future__ import annotations

from typing import TYPE_CHECKING

from app.services.ai.provider import AIProvider, ProviderConfig
from app.services.ai.openai_compatible import OpenAICompatibleProvider

# Importing the tool packages registers their @tool decorators.
from app.services.ai.tools import (  # noqa: F401 — side-effect import
    plan_tools,
    session_tools,
    day_memory_tools,
    project_tools,
    tag_tools,
    memory_tools,
    statistics_tools,
)

if TYPE_CHECKING:
    pass


_PROVIDERS = {
    "openai_compatible": OpenAICompatibleProvider,
}


def get_provider(config: ProviderConfig, kind: str = "openai_compatible") -> AIProvider:
    """Instantiate the configured provider.

    ``kind`` is currently always ``"openai_compatible"``. Add more entries to
    ``_PROVIDERS`` as new vendors are supported.
    """
    if kind not in _PROVIDERS:
        raise ValueError(f"Unknown AI provider kind: {kind!r}. Known: {list(_PROVIDERS)}")
    return _PROVIDERS[kind](config)


__all__ = ["AIProvider", "ProviderConfig", "get_provider"]
