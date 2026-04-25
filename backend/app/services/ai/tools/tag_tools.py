"""Tag tools — read + write."""
from __future__ import annotations

from typing import Optional

from pydantic import BaseModel, Field

from app.services.ai.tools._serialize import serialize_tag
from app.services.ai.tools.registry import ToolContext, tool
from app.services.tag_service import TagService


class ListTagsArgs(BaseModel):
    project_id: Optional[int] = Field(
        default=None,
        description="If set, return tags available for this project (its own + ancestors + globals).",
    )


class CreateTagArgs(BaseModel):
    name: str = Field(..., min_length=1, max_length=100, description="Tag name.")
    color: str = Field(
        ...,
        pattern=r"^#[0-9A-Fa-f]{6}$",
        description="Hex color code in #RRGGBB format (e.g. #10B981).",
    )
    project_id: Optional[int] = Field(
        default=None,
        description="Scope the tag to this project, or null for a global tag.",
    )


@tool(
    name="list_tags",
    description="List tags. With ``project_id``, returns tags usable in that project (inherited).",
    args_model=ListTagsArgs,
    permission_tier="read",
)
def list_tags(ctx: ToolContext, args: ListTagsArgs):
    svc = TagService(ctx.db)
    if args.project_id is not None:
        return [serialize_tag(t) for t in svc.get_available_for_project(args.project_id)]
    return [serialize_tag(t) for t in svc.get_all()]


@tool(
    name="create_tag",
    description=(
        "Create a new tag. Provide a name and a hex color (#RRGGBB). "
        "Set ``project_id`` to scope the tag to a project, or omit it for a global tag."
    ),
    args_model=CreateTagArgs,
    permission_tier="write",
)
def create_tag(ctx: ToolContext, args: CreateTagArgs):
    svc = TagService(ctx.db)
    tag = svc.create(args.model_dump(exclude_none=True))
    return serialize_tag(tag)
