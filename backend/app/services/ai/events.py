"""Vendor-neutral streaming events emitted by AI providers.

A provider's ``stream_chat()`` yields a sequence of these dataclasses; the
agent loop consumes them without knowing which underlying SDK is in play.
"""
from dataclasses import dataclass, field
from typing import Any, Dict, Literal, Optional


@dataclass
class TextDelta:
    """A chunk of assistant text. Multiple of these accumulate into the message body."""
    text: str


@dataclass
class ToolCallStart:
    """Beginning of a tool call. ``id`` is provider-generated; ``name`` is the tool function name."""
    id: str
    name: str


@dataclass
class ToolCallArgsDelta:
    """A fragment of the JSON-encoded args string for a tool call.

    Providers stream these as raw JSON string fragments; we parse them only
    once the matching ``ToolCallEnd`` arrives. ``id`` matches the originating
    ``ToolCallStart.id``.
    """
    id: str
    json_fragment: str


@dataclass
class ToolCallEnd:
    """End of a tool call. ``parsed_args`` is the fully reconstructed args dict.

    May carry ``parse_error`` if the streamed JSON did not parse cleanly.
    """
    id: str
    name: str
    parsed_args: Optional[Dict[str, Any]] = None
    parse_error: Optional[str] = None


@dataclass
class Stop:
    """End-of-turn signal."""
    reason: Literal["end_turn", "tool_use", "max_tokens", "error", "cancelled", "disabled"]
    usage: Optional[Dict[str, int]] = None
    model: Optional[str] = None


@dataclass
class ErrorEvent:
    message: str
    retryable: bool = False
    detail: Dict[str, Any] = field(default_factory=dict)
