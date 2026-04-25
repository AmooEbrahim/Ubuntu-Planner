"""Statistics tools — read-only summaries of completed work."""
from __future__ import annotations

from datetime import date as date_type, timedelta
from typing import Optional

from pydantic import BaseModel, Field

from app.services.ai.tools.registry import ToolContext, tool
from app.services.statistics_service import StatisticsService


def _resolve_range(
    start: Optional[str],
    end: Optional[str],
    default_days: int = 30,
) -> tuple[date_type, date_type]:
    """Coerce optional ISO date strings into ``(start, end)``; default to last N days."""
    end_d = date_type.fromisoformat(end) if end else date_type.today()
    if start:
        start_d = date_type.fromisoformat(start)
    else:
        start_d = end_d - timedelta(days=default_days)
    if start_d > end_d:
        raise ValueError("start date must be on or before end date")
    return start_d, end_d


class _RangeArgs(BaseModel):
    start_date: Optional[str] = Field(
        default=None,
        description="ISO date (YYYY-MM-DD). Inclusive. Defaults to 30 days before end_date.",
    )
    end_date: Optional[str] = Field(
        default=None,
        description="ISO date (YYYY-MM-DD). Inclusive. Defaults to today.",
    )


class StatsOverviewArgs(_RangeArgs):
    pass


class StatsByProjectArgs(_RangeArgs):
    pass


class StatsByTagArgs(_RangeArgs):
    pass


class StatsDailyActivityArgs(_RangeArgs):
    pass


@tool(
    name="stats_overview",
    description=(
        "Summary stats over a date range: total session count, total minutes worked, "
        "average satisfaction (1–5). Defaults to the last 30 days."
    ),
    args_model=StatsOverviewArgs,
    permission_tier="read",
)
def stats_overview(ctx: ToolContext, args: StatsOverviewArgs):
    start, end = _resolve_range(args.start_date, args.end_date)
    svc = StatisticsService(ctx.db)
    out = svc.get_overview(start_date=start, end_date=end)
    out["range"] = {"start": start.isoformat(), "end": end.isoformat()}
    return out


@tool(
    name="stats_by_project",
    description=(
        "Time spent per project over a date range. Returns each project with "
        "session_count, total_minutes, and color, sorted by minutes desc."
    ),
    args_model=StatsByProjectArgs,
    permission_tier="read",
)
def stats_by_project(ctx: ToolContext, args: StatsByProjectArgs):
    start, end = _resolve_range(args.start_date, args.end_date)
    svc = StatisticsService(ctx.db)
    return {
        "range": {"start": start.isoformat(), "end": end.isoformat()},
        "projects": svc.get_by_project(start_date=start, end_date=end),
    }


@tool(
    name="stats_by_tag",
    description=(
        "Time spent per tag over a date range. Useful for cross-project themes. "
        "Returns each tag with session_count, total_minutes, color."
    ),
    args_model=StatsByTagArgs,
    permission_tier="read",
)
def stats_by_tag(ctx: ToolContext, args: StatsByTagArgs):
    start, end = _resolve_range(args.start_date, args.end_date)
    svc = StatisticsService(ctx.db)
    return {
        "range": {"start": start.isoformat(), "end": end.isoformat()},
        "tags": svc.get_by_tag(start_date=start, end_date=end),
    }


@tool(
    name="stats_daily_activity",
    description=(
        "Per-day activity over a date range: session_count, total_minutes, "
        "avg_satisfaction. Returned in date order. Use this to spot trends, gaps, "
        "or weekday patterns."
    ),
    args_model=StatsDailyActivityArgs,
    permission_tier="read",
)
def stats_daily_activity(ctx: ToolContext, args: StatsDailyActivityArgs):
    start, end = _resolve_range(args.start_date, args.end_date)
    svc = StatisticsService(ctx.db)
    return {
        "range": {"start": start.isoformat(), "end": end.isoformat()},
        "days": svc.get_daily_activity(start_date=start, end_date=end),
    }
