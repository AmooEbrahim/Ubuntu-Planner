"""Tag tools — read-only."""
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
