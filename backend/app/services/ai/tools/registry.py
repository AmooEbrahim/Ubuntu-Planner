"""Tool registry.

Tools are decorated functions that the AI agent may call. Each tool declares:

* ``name`` — the callable name the model emits.
* ``description`` — natural-language hint shown to the model.
* ``args_model`` — Pydantic model for the JSON args.
* ``permission_tier`` — ``"read"`` | ``"write"`` | ``"destructive"``.
* ``handler`` — sync function ``(ctx, args) -> Any``. Async handlers are also
  supported and awaited by the executor.

The registry is module-global; tool modules register themselves at import.
"""
from __future__ import annotations

import inspect
import json
from dataclasses import dataclass
from typing import Any, Awaitable, Callable, Dict, List, Optional, Type, Union

from pydantic import BaseModel, ValidationError

from app.services.ai.schema_utils import pydantic_to_openai_schema


PermissionTier = str  # "read" | "write" | "destructive"
PermissionLevel = str  # "allow" | "confirm" | "deny"


DEFAULT_TIER_LEVELS: Dict[PermissionTier, PermissionLevel] = {
    "read": "allow",
    "write": "confirm",
    "destructive": "deny",
}


class EmptyArgs(BaseModel):
    """Args schema for tools that take no parameters."""


@dataclass
class ToolContext:
    """Context passed to every tool handler.

    ``db`` is a SQLAlchemy session — the agent loop opens one per tool call to
    keep transactional scope tight. ``chat_id`` is the active chat for memory
    tools; ``timezone`` (TODO Phase 7) for date-relative tools.
    """

    db: Any
    chat_id: Optional[int] = None
    settings: Optional[Any] = None


HandlerSignature = Callable[[ToolContext, BaseModel], Union[Any, Awaitable[Any]]]


@dataclass
class ToolDef:
    name: str
    description: str
    args_model: Type[BaseModel]
    permission_tier: PermissionTier
    handler: HandlerSignature

    def parameters_schema(self) -> Dict[str, Any]:
        return pydantic_to_openai_schema(self.args_model)

    def to_openai_tool(self) -> Dict[str, Any]:
        return {
            "type": "function",
            "function": {
                "name": self.name,
                "description": self.description,
                "parameters": self.parameters_schema(),
            },
        }


_REGISTRY: Dict[str, ToolDef] = {}


def tool(
    name: str,
    description: str,
    args_model: Type[BaseModel],
    permission_tier: PermissionTier = "read",
):
    """Register a function as an AI tool.

    Example::

        class ListPlansArgs(BaseModel):
            date: Optional[str] = None

        @tool(name="list_plans", description="List planned items.", args_model=ListPlansArgs)
        def list_plans(ctx, args):
            ...
    """
    if permission_tier not in DEFAULT_TIER_LEVELS:
        raise ValueError(f"Unknown permission tier: {permission_tier!r}")

    def decorator(func: HandlerSignature) -> HandlerSignature:
        if name in _REGISTRY:
            raise ValueError(f"Tool {name!r} is already registered.")
        _REGISTRY[name] = ToolDef(
            name=name,
            description=description,
            args_model=args_model,
            permission_tier=permission_tier,
            handler=func,
        )
        return func

    return decorator


def all_tools() -> List[ToolDef]:
    """Return every registered tool (in registration order)."""
    return list(_REGISTRY.values())


def get_tool(name: str) -> Optional[ToolDef]:
    return _REGISTRY.get(name)


def resolve_permission(
    tool_def: ToolDef,
    chat_overrides: Optional[Dict[str, PermissionLevel]],
    global_overrides: Optional[Dict[str, PermissionLevel]],
) -> PermissionLevel:
    """Compute the effective permission for a tool.

    Precedence: chat override → global override → tier default.
    """
    if chat_overrides and tool_def.name in chat_overrides:
        return chat_overrides[tool_def.name]
    if global_overrides and tool_def.name in global_overrides:
        return global_overrides[tool_def.name]
    return DEFAULT_TIER_LEVELS[tool_def.permission_tier]


def visible_tools(
    chat_overrides: Optional[Dict[str, PermissionLevel]] = None,
    global_overrides: Optional[Dict[str, PermissionLevel]] = None,
) -> List[ToolDef]:
    """Tools whose effective level is ``allow`` or ``confirm`` — i.e. exposed to the LLM."""
    out = []
    for t in all_tools():
        level = resolve_permission(t, chat_overrides, global_overrides)
        if level in ("allow", "confirm"):
            out.append(t)
    return out


async def execute_tool(
    tool_name: str,
    raw_args: Union[Dict[str, Any], str, None],
    ctx: ToolContext,
) -> Dict[str, Any]:
    """Validate args, run the handler, return a serializable result envelope.

    Returns ``{"ok": True, "result": ...}`` or ``{"ok": False, "error": str, "type": str}``.
    Always returns — never raises out — so the agent loop can feed the envelope
    back to the model.
    """
    tool_def = get_tool(tool_name)
    if tool_def is None:
        return {
            "ok": False,
            "error": f"Unknown tool {tool_name!r}.",
            "type": "unknown_tool",
            "available": [t.name for t in all_tools()],
        }

    if isinstance(raw_args, str):
        try:
            args_dict = json.loads(raw_args) if raw_args else {}
        except json.JSONDecodeError as exc:
            return {
                "ok": False,
                "error": f"Could not parse tool args as JSON: {exc}",
                "type": "args_parse_error",
            }
    else:
        args_dict = raw_args or {}

    try:
        args = tool_def.args_model(**args_dict)
    except ValidationError as exc:
        return {
            "ok": False,
            "error": "Tool args failed validation.",
            "type": "args_validation_error",
            "detail": exc.errors(),
        }

    try:
        out = tool_def.handler(ctx, args)
        if inspect.isawaitable(out):
            out = await out
    except Exception as exc:  # noqa: BLE001 — feed any tool error back to the model
        return {
            "ok": False,
            "error": str(exc),
            "type": exc.__class__.__name__,
        }

    return {"ok": True, "result": out}


def truncate_result(result: Any, max_bytes: int = 8192) -> Any:
    """Cap the JSON-serialized footprint of a tool result.

    Models can't usefully consume a 200 KB project tree; we serialize, measure,
    and replace with a truncation note when over budget.
    """
    try:
        encoded = json.dumps(result, default=str)
    except (TypeError, ValueError):
        return {"error": "Result is not JSON-serializable.", "type": "serialization_error"}

    if len(encoded) <= max_bytes:
        return result

    keep = max_bytes - 64
    truncated_text = encoded[:keep]
    return {
        "truncated": True,
        "preview": truncated_text,
        "note": f"Result truncated from {len(encoded)} bytes; pass pagination args to fetch more.",
    }
