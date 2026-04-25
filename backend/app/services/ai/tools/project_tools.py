"""Project tools — read + write."""
from __future__ import annotations

from typing import List, Optional

from pydantic import BaseModel, Field

from app.services.ai.tools._serialize import serialize_project, serialize_tag
from app.services.ai.tools.registry import ToolContext, tool
from app.services.project_service import ProjectService


class ListProjectsArgs(BaseModel):
    include_archived: bool = Field(False, description="Include archived projects.")


class GetProjectArgs(BaseModel):
    project_id: int = Field(..., description="Numeric project id.")


class CreateProjectArgs(BaseModel):
    name: str = Field(..., min_length=1, max_length=255, description="Project name.")
    color: str = Field(
        ...,
        pattern=r"^#[0-9A-Fa-f]{6}$",
        description="Hex color code in #RRGGBB format (e.g. #3B82F6).",
    )
    parent_id: Optional[int] = Field(
        default=None,
        description="Parent project id to nest under, or null for a top-level project.",
    )
    description: Optional[str] = Field(default=None, description="Optional free-text description.")
    default_duration: int = Field(
        default=60,
        ge=5,
        description="Default session duration in minutes (used when starting sessions).",
    )
    notification_interval: Optional[int] = Field(
        default=None,
        ge=1,
        description="Minutes between notifications when planned end time is overdue.",
    )
    is_pinned: bool = Field(default=False, description="Pin to the top of project lists.")


@tool(
    name="list_projects",
    description="List the user's projects, including project tags.",
    args_model=ListProjectsArgs,
    permission_tier="read",
)
def list_projects(ctx: ToolContext, args: ListProjectsArgs):
    svc = ProjectService(ctx.db)
    rows = svc.get_all(include_archived=args.include_archived)
    return [
        {**serialize_project(p), "tags": [serialize_tag(t) for t in p.tags]}
        for p in rows
    ]


@tool(
    name="get_project",
    description="Look up a single project by id, with its tags.",
    args_model=GetProjectArgs,
    permission_tier="read",
)
def get_project(ctx: ToolContext, args: GetProjectArgs):
    svc = ProjectService(ctx.db)
    project = svc.get_by_id(args.project_id)
    if project is None:
        raise ValueError(f"Project {args.project_id} not found.")
    return {
        **serialize_project(project),
        "tags": [serialize_tag(t) for t in project.tags],
    }


@tool(
    name="create_project",
    description=(
        "Create a new project. Provide a name and a hex color (#RRGGBB). "
        "Optionally nest under a parent project, set a description, default "
        "session duration, notification interval, or pin it."
    ),
    args_model=CreateProjectArgs,
    permission_tier="write",
)
def create_project(ctx: ToolContext, args: CreateProjectArgs):
    svc = ProjectService(ctx.db)
    project = svc.create(args.model_dump(exclude_none=True))
    return {
        **serialize_project(project),
        "tags": [serialize_tag(t) for t in project.tags],
    }
