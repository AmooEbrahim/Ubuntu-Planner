"""Chat request/response schemas."""
from datetime import datetime
from typing import Any, Dict, List, Literal, Optional

from pydantic import BaseModel, ConfigDict, Field


PermissionLevel = Literal["allow", "confirm", "deny"]


class ChatPermissions(BaseModel):
    """Per-chat overrides keyed by tool name. Missing keys fall back to global."""

    overrides: Dict[str, PermissionLevel] = Field(default_factory=dict)


class ChatCreate(BaseModel):
    title: Optional[str] = None


class ChatUpdate(BaseModel):
    title: Optional[str] = None
    archived: Optional[bool] = None
    permissions: Optional[Dict[str, PermissionLevel]] = None
    system_prompt_override: Optional[str] = None
    model_override: Optional[str] = None


class ChatSummary(BaseModel):
    id: int
    title: str
    archived: bool
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class ChatMessageResponse(BaseModel):
    id: int
    chat_id: int
    parent_message_id: Optional[int]
    role: Literal["system", "user", "assistant", "tool_use", "tool_result"]
    content: Optional[str]
    tool_call_id: Optional[str]
    tool_name: Optional[str]
    tool_args: Optional[Any]
    tool_result: Optional[Any]
    status: Literal["pending", "executing", "complete", "denied", "error", "cancelled"]
    prompt_tokens: Optional[int]
    completion_tokens: Optional[int]
    model: Optional[str]
    suggested_replies: Optional[List[str]] = None
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class ChatDetail(ChatSummary):
    permissions: Optional[Dict[str, PermissionLevel]] = None
    system_prompt_override: Optional[str] = None
    model_override: Optional[str] = None
    messages: List[ChatMessageResponse] = []


class UserMessageCreate(BaseModel):
    content: str = Field(min_length=1)


class ToolDecisionPayload(BaseModel):
    decision: Literal["approve", "deny"]


MemoryTier = Literal["short_term", "mid_term", "long_term", "general"]


class AIMemoryUpsert(BaseModel):
    category: str = Field(default="general", min_length=1, max_length=64)
    key: str = Field(min_length=1, max_length=255)
    value: str
    tier: MemoryTier = "general"


class AIMemoryResponse(BaseModel):
    id: int
    category: str
    key: str
    value: str
    tier: MemoryTier = "general"
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)
