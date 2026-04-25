"""AIProvider abstract base.

Subclasses implement ``stream_chat`` to yield :mod:`events`-typed events
derived from a vendor-specific streaming SDK. The agent loop is provider-blind.
"""
from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Any, AsyncIterator, Dict, List, Optional

from app.services.ai.events import (
    ErrorEvent,
    Stop,
    TextDelta,
    ToolCallArgsDelta,
    ToolCallEnd,
    ToolCallStart,
)
from app.services.ai.tools.registry import ToolDef


# Internal canonical message format passed to providers. Roles are
# ``system``, ``user``, ``assistant``, ``tool``. Provider adapters convert
# this into their native shape.
ProviderMessage = Dict[str, Any]


@dataclass
class ProviderConfig:
    """Connection params for an AI provider."""
    base_url: str
    api_key: str
    model: str
    extra_headers: Optional[Dict[str, str]] = None
    request_timeout: float = 120.0


ProviderEvent = (
    TextDelta
    | ToolCallStart
    | ToolCallArgsDelta
    | ToolCallEnd
    | Stop
    | ErrorEvent
)


class AIProvider(ABC):
    """Abstract async provider streaming chat completions with tool calls."""

    def __init__(self, config: ProviderConfig) -> None:
        self.config = config

    @abstractmethod
    async def stream_chat(
        self,
        messages: List[ProviderMessage],
        tools: List[ToolDef],
    ) -> AsyncIterator[ProviderEvent]:
        """Yield a sequence of events for one model turn.

        Implementations must:
        * always finish with a single ``Stop`` event,
        * emit ``ToolCallEnd`` exactly once per tool call,
        * never raise — wrap exceptions as ``ErrorEvent`` followed by ``Stop(reason='error')``.
        """
        raise NotImplementedError
        yield  # pragma: no cover — for type-check
