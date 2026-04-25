"""Cross-chat AI memory tools.

These let the agent persist small facts across conversations. The total row
count is capped (see :class:`ChatService.AI_MEMORY_CAP`); the loader
prepends only the most-recently-updated entries to the system prompt.

Each memory has a tier:

* ``short_term`` — today / very recent (mood, energy level, "no work today")
* ``mid_term``   — current focus across days/weeks (current project, exam in May)
* ``long_term``  — durable preferences and recurring routines
* ``general``    — anything else
"""
from __future__ import annotations

from typing import Literal, Optional

from pydantic import BaseModel, Field

from app.services.ai.tools.registry import EmptyArgs, ToolContext, tool
from app.services.chat_service import ChatService


ListMemoriesArgs = EmptyArgs

MemoryTier = Literal["short_term", "mid_term", "long_term", "general"]


class SetMemoryArgs(BaseModel):
    category: str = Field(default="general", min_length=1, max_length=64)
    key: str = Field(..., min_length=1, max_length=255)
    value: str = Field(..., description="Free-form text. Keep it short — these go into every system prompt.")
    tier: MemoryTier = Field(
        default="general",
        description=(
            "Lifetime hint. 'short_term' = today / mood / temporary state. "
            "'mid_term' = current focus, ongoing themes (weeks). "
            "'long_term' = durable preferences and recurring routines. "
            "'general' = everything else. Promote/demote a memory by calling this tool again with the same key and a different tier."
        ),
    )


class DeleteMemoryArgs(BaseModel):
    category: str = Field(default="general", min_length=1, max_length=64)
    key: str = Field(..., min_length=1, max_length=255)


@tool(
    name="list_ai_memories",
    description="List your persistent cross-chat memories with their tier and last-updated timestamp.",
    args_model=ListMemoriesArgs,
    permission_tier="read",
)
def list_ai_memories(ctx: ToolContext, _args):
    svc = ChatService(ctx.db)
    rows = svc.list_ai_memories()
    return [
        {
            "category": r.category,
            "key": r.key,
            "value": r.value,
            "tier": getattr(r, "tier", None) or "general",
            "updated_at": r.updated_at.isoformat() if r.updated_at else None,
        }
        for r in rows
    ]


@tool(
    name="set_ai_memory",
    description=(
        "Save or update a small fact you want to remember across chats, with a tier hint "
        "(short_term / mid_term / long_term / general). Use sparingly — these are injected into "
        "every future system prompt. Examples: short_term('mood', 'tired today, low motivation'), "
        "mid_term('current_focus', 'studying for psychology exam in May'), "
        "long_term('routine', 'reads books 09:00-09:50 every weekday')."
    ),
    args_model=SetMemoryArgs,
    permission_tier="write",
)
def set_ai_memory(ctx: ToolContext, args: SetMemoryArgs):
    svc = ChatService(ctx.db)
    row = svc.upsert_ai_memory(args.category, args.key, args.value, args.tier)
    return {
        "category": row.category,
        "key": row.key,
        "value": row.value,
        "tier": row.tier,
    }


@tool(
    name="delete_ai_memory",
    description="Forget a previously stored memory. Destructive — denied by default.",
    args_model=DeleteMemoryArgs,
    permission_tier="destructive",
)
def delete_ai_memory(ctx: ToolContext, args: DeleteMemoryArgs):
    svc = ChatService(ctx.db)
    deleted = svc.delete_ai_memory(args.category, args.key)
    if not deleted:
        raise ValueError(f"Memory ({args.category}, {args.key}) not found.")
    return {"deleted": True}
