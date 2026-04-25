"""Planning tools — read + write."""
from __future__ import annotations

from datetime import date as date_type, datetime
from typing import List, Optional

from pydantic import BaseModel, Field

from app.services.ai.tools._serialize import serialize_planning
from app.services.ai.tools.registry import EmptyArgs, ToolContext, tool
from app.services.planning_service import PlanningService


def _parse_date(value: str) -> date_type:
    return date_type.fromisoformat(value)


def _parse_datetime(value: str) -> datetime:
    """Accept any ISO-8601 datetime and treat the wall-clock parts as local time.

    Why: the rest of the planner stores naive local datetimes (the manual
    create-plan UI sends ``2026-04-26T17:00:00`` with no TZ and that's
    persisted verbatim). Models often append ``Z`` or a UTC offset to the
    same hour the user said, which would convert ``17:00`` to a different
    wall-clock and confuse the user. So we strip TZ and trust the wall
    clock — when the AI says "5pm" the database stores 17:00, exactly
    matching the manual-form behavior.
    """
    if value.endswith("Z"):
        value = value[:-1]
    dt = datetime.fromisoformat(value)
    if dt.tzinfo is not None:
        dt = dt.replace(tzinfo=None)
    return dt


class ListPlansArgs(BaseModel):
    date: Optional[str] = Field(default=None, description="ISO date (YYYY-MM-DD). Omit for all plans.")


class GetPlanArgs(BaseModel):
    planning_id: int = Field(..., description="Numeric planning id.")


class CreatePlanArgs(BaseModel):
    project_id: int
    scheduled_start: str = Field(..., description="Local-time ISO datetime for the start of the slot, e.g. 2026-04-26T17:00:00 — no 'Z' suffix.")
    scheduled_end: str = Field(..., description="Local-time ISO datetime for the end of the slot — same calendar day as start.")
    priority: str = Field(default="medium", description="One of: low, medium, critical.")
    description: Optional[str] = None
    tag_ids: List[int] = Field(default_factory=list)


class CreatePlansBatchArgs(BaseModel):
    plans: List[CreatePlanArgs] = Field(
        ...,
        description="A list of plans to create in a single call. Each entry follows the same shape as create_plan.",
        min_length=1,
        max_length=20,
    )


class UpdatePlanArgs(BaseModel):
    planning_id: int
    project_id: Optional[int] = None
    scheduled_start: Optional[str] = None
    scheduled_end: Optional[str] = None
    priority: Optional[str] = None
    description: Optional[str] = None
    tag_ids: Optional[List[int]] = None


class DeletePlanArgs(BaseModel):
    planning_id: int


@tool(
    name="list_plans",
    description="List planned work items. With ``date`` (YYYY-MM-DD), returns plans for that day.",
    args_model=ListPlansArgs,
    permission_tier="read",
)
def list_plans(ctx: ToolContext, args: ListPlansArgs):
    svc = PlanningService(ctx.db)
    if args.date:
        plans = svc.get_by_date(_parse_date(args.date))
    else:
        plans = svc.get_all()
    return [serialize_planning(p) for p in plans]


@tool(
    name="get_plan",
    description="Look up a single planning item by id.",
    args_model=GetPlanArgs,
    permission_tier="read",
)
def get_plan(ctx: ToolContext, args: GetPlanArgs):
    svc = PlanningService(ctx.db)
    plan = svc.get_by_id(args.planning_id)
    if plan is None:
        raise ValueError(f"Planning {args.planning_id} not found.")
    return serialize_planning(plan)


@tool(
    name="get_active_plan",
    description="Return the planning item whose schedule covers the current moment, or null.",
    args_model=EmptyArgs,
    permission_tier="read",
)
def get_active_plan(ctx: ToolContext, _args):
    svc = PlanningService(ctx.db)
    plan = svc.get_active_now()
    return serialize_planning(plan)


@tool(
    name="create_plan",
    description="Schedule a new work item. Both endpoints must be the same calendar day and not overlap an existing plan.",
    args_model=CreatePlanArgs,
    permission_tier="write",
)
def create_plan(ctx: ToolContext, args: CreatePlanArgs):
    svc = PlanningService(ctx.db)
    payload = {
        "project_id": args.project_id,
        "scheduled_start": _parse_datetime(args.scheduled_start),
        "scheduled_end": _parse_datetime(args.scheduled_end),
        "priority": args.priority,
        "description": args.description,
        "tag_ids": args.tag_ids,
    }
    plan = svc.create(payload)
    return serialize_planning(plan)


@tool(
    name="create_plans",
    description=(
        "Create multiple planning items in one call. Each entry has the same shape as create_plan. "
        "All entries are created in order; if any one fails (overlap, validation), the rest already "
        "created are kept and the failure is reported in the per-entry result."
    ),
    args_model=CreatePlansBatchArgs,
    permission_tier="write",
)
def create_plans(ctx: ToolContext, args: CreatePlansBatchArgs):
    svc = PlanningService(ctx.db)
    out = []
    for entry in args.plans:
        payload = {
            "project_id": entry.project_id,
            "scheduled_start": _parse_datetime(entry.scheduled_start),
            "scheduled_end": _parse_datetime(entry.scheduled_end),
            "priority": entry.priority,
            "description": entry.description,
            "tag_ids": entry.tag_ids,
        }
        try:
            plan = svc.create(payload)
            out.append({"ok": True, "plan": serialize_planning(plan)})
        except ValueError as exc:
            out.append({"ok": False, "error": str(exc), "input": entry.model_dump()})
    return {"created": sum(1 for r in out if r["ok"]), "results": out}


@tool(
    name="update_plan",
    description="Update an existing planning item. Only provided fields are changed.",
    args_model=UpdatePlanArgs,
    permission_tier="write",
)
def update_plan(ctx: ToolContext, args: UpdatePlanArgs):
    svc = PlanningService(ctx.db)
    patch = args.model_dump(exclude_unset=True, exclude_none=True)
    patch.pop("planning_id", None)
    if "scheduled_start" in patch:
        patch["scheduled_start"] = _parse_datetime(patch["scheduled_start"])
    if "scheduled_end" in patch:
        patch["scheduled_end"] = _parse_datetime(patch["scheduled_end"])
    plan = svc.update(args.planning_id, patch)
    return serialize_planning(plan)


@tool(
    name="delete_plan",
    description="Delete a planning item permanently. Destructive — denied by default.",
    args_model=DeletePlanArgs,
    permission_tier="destructive",
)
def delete_plan(ctx: ToolContext, args: DeletePlanArgs):
    svc = PlanningService(ctx.db)
    deleted = svc.delete(args.planning_id)
    if not deleted:
        raise ValueError(f"Planning {args.planning_id} not found.")
    return {"deleted": True, "planning_id": args.planning_id}
