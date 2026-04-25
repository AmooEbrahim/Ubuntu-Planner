"""Day-memory tools — read + write across user / AI tracks."""
from __future__ import annotations

from datetime import date as date_type
from typing import Optional

from pydantic import BaseModel, Field

from app.services.ai.tools._serialize import serialize_day_memory
from app.services.ai.tools.registry import ToolContext, tool
from app.services.day_memory_service import DayMemoryService


def _parse_date(value: Optional[str]) -> date_type:
    return date_type.fromisoformat(value) if value else date_type.today()


class GetDayMemoryArgs(BaseModel):
    date: Optional[str] = Field(default=None, description="ISO date (YYYY-MM-DD). Defaults to today.")


class UpsertSectionArgs(BaseModel):
    date: Optional[str] = Field(default=None, description="ISO date. Defaults to today.")
    intentions: Optional[str] = None
    reflection: Optional[str] = None
    lessons: Optional[str] = None
    completed: Optional[str] = None
    gratitude: Optional[str] = None
    free_notes: Optional[str] = None
    mood: Optional[int] = Field(default=None, ge=1, le=5)


@tool(
    name="get_day_memory",
    description=(
        "Return the user's and AI's day-memory tracks for a date. "
        "Both tracks are returned so you can reflect on the user's notes."
    ),
    args_model=GetDayMemoryArgs,
    permission_tier="read",
)
def get_day_memory(ctx: ToolContext, args: GetDayMemoryArgs):
    svc = DayMemoryService(ctx.db)
    target = _parse_date(args.date)
    user_row, ai_row = svc.get_pair(target)
    return {
        "date": target.isoformat(),
        "user": serialize_day_memory(user_row),
        "ai": serialize_day_memory(ai_row),
    }


@tool(
    name="upsert_day_memory_ai_track",
    description=(
        "Add or update the AI's track for a date. Use this to record your own observations, "
        "patterns you noticed, or follow-up suggestions — separate from the user's own journal."
    ),
    args_model=UpsertSectionArgs,
    permission_tier="write",
)
def upsert_day_memory_ai_track(ctx: ToolContext, args: UpsertSectionArgs):
    svc = DayMemoryService(ctx.db)
    target = _parse_date(args.date)
    payload = {
        k: v
        for k, v in args.model_dump(exclude_unset=True).items()
        if k != "date"
    }
    row = svc.upsert(target, is_ai=True, data=payload)
    return serialize_day_memory(row)


@tool(
    name="upsert_day_memory_user_track",
    description=(
        "Edit the user's own day-memory track. Sensitive — denied by default. "
        "Only use if the user explicitly asks you to write into their personal journal."
    ),
    args_model=UpsertSectionArgs,
    permission_tier="destructive",
)
def upsert_day_memory_user_track(ctx: ToolContext, args: UpsertSectionArgs):
    svc = DayMemoryService(ctx.db)
    target = _parse_date(args.date)
    payload = {
        k: v
        for k, v in args.model_dump(exclude_unset=True).items()
        if k != "date"
    }
    row = svc.upsert(target, is_ai=False, data=payload)
    return serialize_day_memory(row)
