"""Session tools — read + write."""
from __future__ import annotations

from typing import List, Optional

from pydantic import BaseModel, Field

from app.services.ai.tools._serialize import serialize_session
from app.services.ai.tools.registry import EmptyArgs, ToolContext, tool
from app.services.session_service import SessionService


class ListSessionsArgs(BaseModel):
    limit: int = Field(default=20, ge=1, le=100, description="Max recent sessions to return.")


class GetSessionArgs(BaseModel):
    session_id: int


class StartSessionArgs(BaseModel):
    project_id: Optional[int] = Field(default=None, description="Project to attribute work to.")
    planned_duration: int = Field(..., ge=1, le=12 * 60, description="Planned duration in minutes.")
    planning_id: Optional[int] = Field(default=None, description="Optional source planning row.")
    tag_ids: List[int] = Field(default_factory=list)
    notes: Optional[str] = None


class EndSessionArgs(BaseModel):
    session_id: int
    notes: Optional[str] = None
    satisfaction_score: Optional[int] = Field(default=None, ge=1, le=5)
    tasks_done: Optional[str] = None


class UpdateSessionArgs(BaseModel):
    session_id: int
    notes: Optional[str] = None
    satisfaction_score: Optional[int] = Field(default=None, ge=1, le=5)
    tasks_done: Optional[str] = None
    project_id: Optional[int] = None
    tag_ids: Optional[List[int]] = None


class DeleteSessionArgs(BaseModel):
    session_id: int


@tool(
    name="get_active_session",
    description="Return the currently running session, or null if none is active.",
    args_model=EmptyArgs,
    permission_tier="read",
)
def get_active_session(ctx: ToolContext, _args):
    svc = SessionService(ctx.db)
    return serialize_session(svc.get_active_session())


@tool(
    name="list_sessions",
    description="List recent completed sessions, newest first.",
    args_model=ListSessionsArgs,
    permission_tier="read",
)
def list_sessions(ctx: ToolContext, args: ListSessionsArgs):
    svc = SessionService(ctx.db)
    return [serialize_session(s) for s in svc.get_recent(limit=args.limit)]


@tool(
    name="get_session",
    description="Look up a single session by id.",
    args_model=GetSessionArgs,
    permission_tier="read",
)
def get_session(ctx: ToolContext, args: GetSessionArgs):
    svc = SessionService(ctx.db)
    session = svc.get_by_id(args.session_id)
    if session is None:
        raise ValueError(f"Session {args.session_id} not found.")
    return serialize_session(session)


@tool(
    name="start_session",
    description="Start a new work session. Fails if another session is still active.",
    args_model=StartSessionArgs,
    permission_tier="write",
)
def start_session(ctx: ToolContext, args: StartSessionArgs):
    svc = SessionService(ctx.db)
    payload = args.model_dump(exclude_none=True)
    session = svc.start_session(payload)
    return serialize_session(session)


@tool(
    name="end_session",
    description="Stop a running session, optionally attaching review fields.",
    args_model=EndSessionArgs,
    permission_tier="write",
)
def end_session(ctx: ToolContext, args: EndSessionArgs):
    svc = SessionService(ctx.db)
    review = {k: v for k, v in args.model_dump(exclude_unset=True).items() if k != "session_id"}
    session = svc.stop_session(args.session_id, review_data=review or None)
    return serialize_session(session)


@tool(
    name="update_session",
    description="Update fields on an existing session (notes, satisfaction, tags, etc.).",
    args_model=UpdateSessionArgs,
    permission_tier="write",
)
def update_session(ctx: ToolContext, args: UpdateSessionArgs):
    svc = SessionService(ctx.db)
    patch = {k: v for k, v in args.model_dump(exclude_unset=True).items() if k != "session_id"}
    session = svc.update_session(args.session_id, patch)
    return serialize_session(session)


@tool(
    name="delete_session",
    description="Delete a session permanently. Destructive — denied by default.",
    args_model=DeleteSessionArgs,
    permission_tier="destructive",
)
def delete_session(ctx: ToolContext, args: DeleteSessionArgs):
    svc = SessionService(ctx.db)
    svc.delete_session(args.session_id)
    return {"deleted": True, "session_id": args.session_id}
