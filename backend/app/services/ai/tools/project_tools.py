"""Project tools — read-only."""
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
