"""AI settings schemas."""
from typing import Any, Dict, Literal, Optional

from pydantic import BaseModel, Field


PermissionLevel = Literal["allow", "confirm", "deny"]


class AISettingsResponse(BaseModel):
    enabled: bool
    provider: str
    model: str
    base_url: str
    api_key: str
    system_prompt: str
    user_prompt: str = ""
    permissions: Dict[str, PermissionLevel] = Field(default_factory=dict)
    max_tool_iterations: int
    request_timeout: int


class AISettingsUpdate(BaseModel):
    enabled: Optional[bool] = None
    provider: Optional[str] = None
    model: Optional[str] = None
    base_url: Optional[str] = None
    api_key: Optional[str] = None
    system_prompt: Optional[str] = None
    user_prompt: Optional[str] = None
    permissions: Optional[Dict[str, PermissionLevel]] = None
    max_tool_iterations: Optional[int] = Field(default=None, ge=1, le=50)
    request_timeout: Optional[int] = Field(default=None, ge=10, le=600)


class ToolDescriptor(BaseModel):
    name: str
    description: str
    permission_tier: str
    default_level: PermissionLevel
