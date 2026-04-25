"""OpenAI-compatible provider.

Works against any endpoint that speaks the OpenAI Chat Completions API:
OpenAI, OpenRouter, Ollama, LocalAI, Groq, vLLM, etc. Uses the official
``openai`` Python SDK with a configurable ``base_url``.
"""
from __future__ import annotations

import json
from typing import Any, AsyncIterator, Dict, List, Optional

from openai import AsyncOpenAI, OpenAIError

from app.services.ai.events import (
    ErrorEvent,
    Stop,
    TextDelta,
    ToolCallArgsDelta,
    ToolCallEnd,
    ToolCallStart,
)
from app.services.ai.provider import (
    AIProvider,
    ProviderConfig,
    ProviderEvent,
    ProviderMessage,
)
from app.services.ai.tools.registry import ToolDef


class OpenAICompatibleProvider(AIProvider):
    """Streaming wrapper around ``openai.AsyncOpenAI``."""

    def __init__(self, config: ProviderConfig) -> None:
        super().__init__(config)
        self._client = AsyncOpenAI(
            api_key=config.api_key or "missing",
            base_url=config.base_url,
            default_headers=config.extra_headers,
            timeout=config.request_timeout,
        )

    async def stream_chat(
        self,
        messages: List[ProviderMessage],
        tools: List[ToolDef],
    ) -> AsyncIterator[ProviderEvent]:
        openai_tools = [t.to_openai_tool() for t in tools] if tools else None
        payload: Dict[str, Any] = {
            "model": self.config.model,
            "messages": _to_openai_messages(messages),
            "stream": True,
            "stream_options": {"include_usage": True},
        }
        if openai_tools:
            payload["tools"] = openai_tools

        try:
            response = await self._client.chat.completions.create(**payload)
        except OpenAIError as exc:
            yield ErrorEvent(message=str(exc), retryable=False)
            yield Stop(reason="error")
            return
        except Exception as exc:  # pragma: no cover — defensive
            yield ErrorEvent(message=f"Unexpected error: {exc}", retryable=False)
            yield Stop(reason="error")
            return

        # State for in-flight tool calls (keyed by index because some providers
        # don't include the id in every delta).
        active_tool_calls: Dict[int, _ToolCallInProgress] = {}
        finish_reason: Optional[str] = None
        usage_payload: Optional[Dict[str, int]] = None
        seen_text: bool = False

        try:
            async for chunk in response:
                if chunk.usage is not None:
                    usage_payload = {
                        "prompt_tokens": chunk.usage.prompt_tokens or 0,
                        "completion_tokens": chunk.usage.completion_tokens or 0,
                        "total_tokens": chunk.usage.total_tokens or 0,
                    }
                if not chunk.choices:
                    continue
                choice = chunk.choices[0]
                delta = choice.delta

                if delta and delta.content:
                    seen_text = True
                    yield TextDelta(text=delta.content)

                if delta and delta.tool_calls:
                    for tc_delta in delta.tool_calls:
                        idx = tc_delta.index
                        in_progress = active_tool_calls.get(idx)

                        # Start a new tool call when we see an id and we haven't already.
                        if in_progress is None:
                            tc_id = tc_delta.id or f"tc_{idx}"
                            tc_name = (tc_delta.function.name if tc_delta.function else None) or ""
                            in_progress = _ToolCallInProgress(id=tc_id, name=tc_name)
                            active_tool_calls[idx] = in_progress
                            if tc_name:
                                yield ToolCallStart(id=tc_id, name=tc_name)
                        else:
                            # Some providers backfill name/id in later chunks.
                            if not in_progress.name and tc_delta.function and tc_delta.function.name:
                                in_progress.name = tc_delta.function.name
                                yield ToolCallStart(id=in_progress.id, name=in_progress.name)
                            if not in_progress.id and tc_delta.id:
                                in_progress.id = tc_delta.id

                        fn = tc_delta.function
                        if fn and fn.arguments:
                            in_progress.args_buffer += fn.arguments
                            yield ToolCallArgsDelta(
                                id=in_progress.id,
                                json_fragment=fn.arguments,
                            )

                if choice.finish_reason:
                    finish_reason = choice.finish_reason

        except Exception as exc:  # noqa: BLE001
            yield ErrorEvent(message=f"Stream error: {exc}", retryable=True)
            yield Stop(reason="error", usage=usage_payload, model=self.config.model)
            return

        # Emit ToolCallEnd for every collected tool call.
        for in_progress in active_tool_calls.values():
            parsed: Optional[Dict[str, Any]] = None
            parse_error: Optional[str] = None
            try:
                parsed = json.loads(in_progress.args_buffer) if in_progress.args_buffer else {}
            except json.JSONDecodeError as exc:
                parse_error = str(exc)
            yield ToolCallEnd(
                id=in_progress.id,
                name=in_progress.name,
                parsed_args=parsed,
                parse_error=parse_error,
            )

        normalized_reason = _normalize_finish_reason(finish_reason, has_tool_calls=bool(active_tool_calls), seen_text=seen_text)
        yield Stop(reason=normalized_reason, usage=usage_payload, model=self.config.model)


class _ToolCallInProgress:
    __slots__ = ("id", "name", "args_buffer")

    def __init__(self, id: str, name: str) -> None:
        self.id = id
        self.name = name
        self.args_buffer = ""


def _normalize_finish_reason(
    reason: Optional[str],
    *,
    has_tool_calls: bool,
    seen_text: bool,
):
    if reason == "tool_calls" or has_tool_calls:
        return "tool_use"
    if reason == "length":
        return "max_tokens"
    if reason == "stop":
        return "end_turn"
    if reason is None and seen_text:
        return "end_turn"
    return reason or "end_turn"


def _to_openai_messages(messages: List[ProviderMessage]) -> List[Dict[str, Any]]:
    """Translate our internal canonical messages into OpenAI shape.

    Internal canonical roles: system, user, assistant, tool. Assistant messages
    may carry a ``tool_calls`` list. Tool messages carry ``tool_call_id`` and
    ``content`` (stringified result).
    """
    out: List[Dict[str, Any]] = []
    for m in messages:
        role = m.get("role")
        if role == "tool":
            out.append({
                "role": "tool",
                "tool_call_id": m.get("tool_call_id", ""),
                "content": m.get("content", ""),
            })
        elif role == "assistant":
            entry: Dict[str, Any] = {"role": "assistant", "content": m.get("content") or None}
            tool_calls = m.get("tool_calls")
            if tool_calls:
                entry["tool_calls"] = [
                    {
                        "id": tc["id"],
                        "type": "function",
                        "function": {
                            "name": tc["name"],
                            "arguments": tc.get("arguments_json")
                            or json.dumps(tc.get("arguments", {})),
                        },
                    }
                    for tc in tool_calls
                ]
            out.append(entry)
        else:
            out.append({"role": role, "content": m.get("content", "")})
    return out
