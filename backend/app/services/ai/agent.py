"""Agent orchestrator.

The :class:`AgentRunner` owns the multi-iteration tool-calling loop. It is
provider-agnostic — given an :class:`~app.services.ai.provider.AIProvider`,
it streams a single user turn until the model says it's done, a tool needs
confirmation, the iteration cap is hit, the user cancels, or AI is disabled.

The runner emits high-level :mod:`stream_events` records via an async
generator. The SSE endpoint serializes those into ``text/event-stream``.
"""
from __future__ import annotations

import asyncio
import json
import time
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, AsyncGenerator, Dict, List, Optional

from fastapi.concurrency import run_in_threadpool

from app.core.database import SessionLocal
from app.services.ai import get_provider
from app.services.ai.events import (
    ErrorEvent,
    Stop,
    TextDelta,
    ToolCallArgsDelta,
    ToolCallEnd,
    ToolCallStart,
)
from app.services.ai.provider import ProviderConfig
from app.services.ai.tools.registry import (
    ToolContext,
    execute_tool,
    resolve_permission,
    truncate_result,
    visible_tools,
)
from app.services.ai_settings_service import AISettingsService
from app.services.chat_service import ChatService


# ----------------- High-level streaming events -----------------


@dataclass
class StreamEvent:
    """Discriminated union by ``type``."""
    type: str
    data: Dict[str, Any] = field(default_factory=dict)


# ----------------- Cancellation registry -----------------


_active_turns: Dict[int, asyncio.Event] = {}


def is_turn_active(chat_id: int) -> bool:
    return chat_id in _active_turns


def cancel_turn(chat_id: int) -> bool:
    """Signal cancellation. Returns True if a turn was running."""
    cancel = _active_turns.get(chat_id)
    if cancel is None:
        return False
    cancel.set()
    return True


# ----------------- Agent runner -----------------


MAX_HISTORY_MESSAGES = 80
MAX_ASSISTANT_BUFFER = 400_000  # Hard sanity cap on a single streamed message.

# Token budget driving history compaction. ~4 chars per token is a rough
# estimate that holds across most tokenizers. We compact when the projected
# prompt exceeds ``COMPACT_BUDGET_CHARS`` so the model gets enough headroom
# to think + produce output. Tunable via ``ai.max_history_chars`` setting
# in the future.
COMPACT_BUDGET_CHARS = 80_000  # ~20k tokens
COMPACT_KEEP_RECENT = 10  # Always keep the last N messages verbatim.


class AgentRunner:
    """Orchestrates one user turn through the tool-calling loop."""

    async def stream_turn(
        self,
        chat_id: int,
        user_content: Optional[str],
        *,
        resume: bool = False,
    ) -> AsyncGenerator[StreamEvent, None]:
        """Append a user message (unless resuming) and stream until terminal.

        Yields :class:`StreamEvent` records. Always finishes with a ``done`` event.
        """
        if chat_id in _active_turns:
            yield StreamEvent("error", {"message": "A turn is already streaming for this chat."})
            yield StreamEvent("done", {"reason": "conflict"})
            return

        cancel_event = asyncio.Event()
        _active_turns[chat_id] = cancel_event

        try:
            async for ev in self._run(chat_id, user_content, resume=resume, cancel=cancel_event):
                yield ev
        finally:
            _active_turns.pop(chat_id, None)

    # ---- Internal ----

    async def _run(
        self,
        chat_id: int,
        user_content: Optional[str],
        *,
        resume: bool,
        cancel: asyncio.Event,
    ) -> AsyncGenerator[StreamEvent, None]:
        config = await run_in_threadpool(self._load_config)
        if not config["enabled"]:
            yield StreamEvent("error", {"message": "AI is disabled. Enable it in /settings/ai."})
            yield StreamEvent("done", {"reason": "disabled"})
            return
        if not config["api_key"]:
            yield StreamEvent(
                "error",
                {"message": "AI is enabled but no API key is set. Configure it in /settings/ai."},
            )
            yield StreamEvent("done", {"reason": "error"})
            return

        chat = await run_in_threadpool(self._load_chat, chat_id)
        if chat is None:
            yield StreamEvent("error", {"message": "Chat not found."})
            yield StreamEvent("done", {"reason": "error"})
            return

        if not resume and user_content is not None:
            user_msg = await run_in_threadpool(
                self._append_message, chat_id, role="user", content=user_content,
            )
            yield StreamEvent("message", _serialize_message(user_msg))

        # Block sending if we have unresolved pending tool calls.
        pending = await run_in_threadpool(self._get_pending_tool_calls, chat_id)
        if pending and not resume:
            yield StreamEvent(
                "error",
                {"message": "There is a pending tool call awaiting your decision. Resolve it first."},
            )
            yield StreamEvent("done", {"reason": "blocked"})
            return

        provider = get_provider(
            ProviderConfig(
                base_url=config["base_url"],
                api_key=config["api_key"],
                model=chat.model_override or config["model"],
                request_timeout=float(config["request_timeout"]),
                extra_headers=_build_extra_headers(config),
            ),
            kind=config["provider"],
        )

        max_iterations = int(config["max_tool_iterations"])
        chat_perms = chat.permissions if isinstance(chat.permissions, dict) else None
        global_perms = config.get("permissions") or {}

        for iteration in range(max_iterations):
            if cancel.is_set():
                yield StreamEvent("done", {"reason": "cancelled"})
                return

            # Reload provider message history each iteration (rehydrate from DB).
            messages = await run_in_threadpool(
                self._build_provider_messages, chat_id, config, chat,
            )
            visible = visible_tools(
                chat_overrides=chat_perms,
                global_overrides=global_perms,
            )

            assistant_msg_id: Optional[int] = None
            text_buffer = ""
            tool_calls_meta: Dict[str, Dict[str, Any]] = {}
            tool_call_order: List[str] = []
            usage_payload: Optional[Dict[str, int]] = None
            stop_reason: str = "end_turn"
            stop_model: Optional[str] = None

            try:
                async for ev in provider.stream_chat(messages, visible):
                    if cancel.is_set():
                        break

                    if isinstance(ev, TextDelta):
                        if assistant_msg_id is None:
                            assistant = await run_in_threadpool(
                                self._append_message,
                                chat_id,
                                role="assistant",
                                content="",
                                model=chat.model_override or config["model"],
                            )
                            assistant_msg_id = assistant.id
                            yield StreamEvent("assistant_started", {"message_id": assistant_msg_id})
                        text_buffer += ev.text
                        if len(text_buffer) > MAX_ASSISTANT_BUFFER:
                            text_buffer = text_buffer[-MAX_ASSISTANT_BUFFER:]
                        yield StreamEvent(
                            "text",
                            {"message_id": assistant_msg_id, "delta": ev.text},
                        )
                    elif isinstance(ev, ToolCallStart):
                        tool_calls_meta[ev.id] = {
                            "id": ev.id,
                            "name": ev.name,
                            "args_buffer": "",
                            "parsed_args": None,
                            "parse_error": None,
                        }
                        tool_call_order.append(ev.id)
                        yield StreamEvent(
                            "tool_call_start",
                            {"tool_call_id": ev.id, "tool_name": ev.name},
                        )
                    elif isinstance(ev, ToolCallArgsDelta):
                        meta = tool_calls_meta.setdefault(
                            ev.id,
                            {"id": ev.id, "name": "", "args_buffer": "", "parsed_args": None, "parse_error": None},
                        )
                        meta["args_buffer"] += ev.json_fragment
                        yield StreamEvent(
                            "tool_call_args",
                            {"tool_call_id": ev.id, "fragment": ev.json_fragment},
                        )
                    elif isinstance(ev, ToolCallEnd):
                        meta = tool_calls_meta.setdefault(
                            ev.id,
                            {"id": ev.id, "name": ev.name, "args_buffer": "", "parsed_args": None, "parse_error": None},
                        )
                        meta["name"] = ev.name or meta.get("name") or ""
                        meta["parsed_args"] = ev.parsed_args
                        meta["parse_error"] = ev.parse_error
                    elif isinstance(ev, Stop):
                        stop_reason = ev.reason
                        usage_payload = ev.usage
                        stop_model = ev.model
                    elif isinstance(ev, ErrorEvent):
                        yield StreamEvent("error", {"message": ev.message})
            except Exception as exc:  # noqa: BLE001
                yield StreamEvent("error", {"message": f"Provider stream failed: {exc}"})
                stop_reason = "error"

            # Persist assistant text + usage.
            if assistant_msg_id is not None:
                await run_in_threadpool(
                    self._update_message,
                    assistant_msg_id,
                    {
                        "content": text_buffer,
                        "prompt_tokens": (usage_payload or {}).get("prompt_tokens"),
                        "completion_tokens": (usage_payload or {}).get("completion_tokens"),
                        "model": stop_model,
                    },
                )
                yield StreamEvent(
                    "assistant_complete",
                    {"message_id": assistant_msg_id, "content": text_buffer, "usage": usage_payload},
                )

            if cancel.is_set():
                yield StreamEvent("done", {"reason": "cancelled"})
                return

            if stop_reason == "error":
                yield StreamEvent("done", {"reason": "error", "usage": usage_payload})
                return

            if not tool_call_order:
                # Final assistant turn — try to generate quick-reply suggestions.
                if (
                    stop_reason == "end_turn"
                    and assistant_msg_id is not None
                    and text_buffer.strip()
                ):
                    suggestions = await self._generate_suggestions(provider, messages, text_buffer)
                    if suggestions:
                        await run_in_threadpool(
                            self._update_message,
                            assistant_msg_id,
                            {"suggested_replies": suggestions},
                        )
                        yield StreamEvent(
                            "suggested_replies",
                            {"message_id": assistant_msg_id, "suggestions": suggestions},
                        )
                yield StreamEvent("done", {"reason": stop_reason, "usage": usage_payload})
                return

            # Process each tool call in order.
            paused = False
            for tc_id in tool_call_order:
                meta = tool_calls_meta[tc_id]
                tool_name = meta["name"]
                args = _resolve_tool_args(meta)

                tool_use_msg = await run_in_threadpool(
                    self._append_message,
                    chat_id,
                    role="tool_use",
                    parent_message_id=assistant_msg_id,
                    tool_call_id=tc_id,
                    tool_name=tool_name,
                    tool_args=args if not meta["parse_error"] else {"_raw": meta["args_buffer"], "_parse_error": meta["parse_error"]},
                    status="pending",
                )

                effective_level = _effective_permission_for(
                    tool_name, chat_perms, global_perms,
                )
                yield StreamEvent(
                    "tool_call",
                    {
                        "id": tool_use_msg.id,
                        "tool_call_id": tc_id,
                        "tool_name": tool_name,
                        "args": args,
                        "status": "pending",
                        "permission": effective_level,
                    },
                )

                if meta["parse_error"]:
                    fake_result = {"ok": False, "error": "Args JSON parse failed.", "type": "args_parse_error", "detail": meta["parse_error"]}
                    await self._record_tool_result(
                        chat_id, tc_id, tool_use_msg.id, "error", fake_result,
                    )
                    yield StreamEvent(
                        "tool_result",
                        {"tool_call_id": tc_id, "tool_use_id": tool_use_msg.id, "status": "error", "result": fake_result},
                    )
                    continue

                if effective_level == "deny":
                    fake_result = {"ok": False, "error": "Tool denied by permission policy.", "type": "permission_denied"}
                    await self._record_tool_result(
                        chat_id, tc_id, tool_use_msg.id, "denied", fake_result,
                    )
                    yield StreamEvent(
                        "tool_result",
                        {"tool_call_id": tc_id, "tool_use_id": tool_use_msg.id, "status": "denied", "result": fake_result},
                    )
                    continue

                if effective_level == "confirm":
                    yield StreamEvent(
                        "pending_confirmation",
                        {"tool_call_id": tc_id, "tool_use_id": tool_use_msg.id, "tool_name": tool_name, "args": args},
                    )
                    paused = True
                    break

                # allow → execute now.
                await run_in_threadpool(self._mark_executing, tool_use_msg.id)
                yield StreamEvent("tool_call", {"id": tool_use_msg.id, "tool_call_id": tc_id, "status": "executing"})
                envelope = await self._execute_tool_in_thread(tool_name, args, chat_id)
                envelope_truncated = truncate_result(envelope, max_bytes=8192)
                status = "complete" if envelope.get("ok") else "error"
                await self._record_tool_result(
                    chat_id, tc_id, tool_use_msg.id, status, envelope_truncated,
                )
                yield StreamEvent(
                    "tool_result",
                    {"tool_call_id": tc_id, "tool_use_id": tool_use_msg.id, "status": status, "result": envelope_truncated},
                )

            if paused:
                yield StreamEvent("done", {"reason": "pending_confirmation"})
                return

            # Loop and let the model see tool results.

        yield StreamEvent(
            "error",
            {"message": f"Reached the {max_iterations}-iteration cap. Reply 'continue' to keep going."},
        )
        yield StreamEvent("done", {"reason": "max_iterations"})

    # ---- Sync helpers (run in threadpool) ----

    def _load_config(self) -> Dict[str, Any]:
        with SessionLocal() as db:
            return AISettingsService(db).get_config()

    def _load_chat(self, chat_id: int):
        with SessionLocal() as db:
            chat = ChatService(db).get_chat(chat_id)
            if chat is None:
                return None
            db.expunge(chat)
            return chat

    def _append_message(self, chat_id: int, **fields) -> Any:
        with SessionLocal() as db:
            msg = ChatService(db).append_message(chat_id, **fields)
            db.expunge(msg)
            return msg

    def _update_message(self, message_id: int, fields: Dict[str, Any]) -> None:
        with SessionLocal() as db:
            ChatService(db).update_message(message_id, fields)

    def _mark_executing(self, message_id: int) -> None:
        self._update_message(message_id, {"status": "executing"})

    def _get_pending_tool_calls(self, chat_id: int) -> List[Any]:
        with SessionLocal() as db:
            rows = ChatService(db).get_pending_tool_calls(chat_id)
            for r in rows:
                db.expunge(r)
            return rows

    def _build_provider_messages(self, chat_id: int, config: Dict[str, Any], chat) -> List[Dict[str, Any]]:
        """Build the canonical message list to send to the provider."""
        with SessionLocal() as db:
            chat_service = ChatService(db)
            db_messages = chat_service.list_messages(chat_id)
            db_messages = db_messages[-MAX_HISTORY_MESSAGES:]
            ai_memories = chat_service.list_ai_memories_for_prompt()

        db_messages = _compact_history(db_messages)

        sections: List[str] = []
        sections.append((chat.system_prompt_override or config.get("system_prompt") or "").strip())

        user_prompt = (config.get("user_prompt") or "").strip()
        if user_prompt:
            sections.append(f"About the user (their own preferences, context, and instructions):\n{user_prompt}")

        if ai_memories:
            sections.append(_format_ai_memories(ai_memories))

        sections.append(_current_time_context())
        system_prompt = "\n\n".join(s for s in sections if s)

        out: List[Dict[str, Any]] = [{"role": "system", "content": system_prompt}]

        # Group tool_use rows by parent_message_id to attach as tool_calls on the assistant.
        tool_uses_by_assistant: Dict[int, List[Any]] = {}
        for m in db_messages:
            if m.role == "tool_use" and m.parent_message_id:
                tool_uses_by_assistant.setdefault(m.parent_message_id, []).append(m)

        for m in db_messages:
            if m.role == "user":
                stamp = _format_user_timestamp(getattr(m, "created_at", None))
                content = m.content or ""
                if stamp:
                    content = f"[sent {stamp}]\n{content}"
                out.append({"role": "user", "content": content})
            elif m.role == "assistant":
                tool_calls_for_msg = tool_uses_by_assistant.get(m.id, [])
                entry: Dict[str, Any] = {
                    "role": "assistant",
                    "content": m.content or None,
                }
                if tool_calls_for_msg:
                    entry["tool_calls"] = [
                        {
                            "id": tu.tool_call_id,
                            "name": tu.tool_name or "",
                            "arguments": tu.tool_args or {},
                        }
                        for tu in tool_calls_for_msg
                    ]
                out.append(entry)
            elif m.role == "tool_result":
                out.append({
                    "role": "tool",
                    "tool_call_id": m.tool_call_id or "",
                    "content": _format_tool_result_for_model(m.tool_result),
                })
            # tool_use rows are folded into the assistant entry; system is ignored.

        return out

    async def _generate_suggestions(
        self,
        provider,
        prior_messages: List[Dict[str, Any]],
        latest_assistant_text: str,
    ) -> List[str]:
        """Make a small follow-up completion to suggest 0–3 next-replies.

        Uses the same provider/model as the main turn but with no tools and a
        short, JSON-targeted system prompt. Failure modes (model returning
        prose, malformed JSON, network blip) all silently produce no
        suggestions — this feature must never break the main turn.
        """
        instruction = (
            "You will be shown a conversation between the user and an assistant. "
            "Your job is to suggest 0 to 3 very short follow-up replies the user "
            "might naturally type next, based on the assistant's last message. "
            "Each suggestion must be under 60 characters, in the user's voice "
            "(first person), and useful to click as a quick reply. Do not repeat "
            "the assistant's own text. If the conversation is closed and no "
            "follow-up makes sense, return an empty list. "
            'Reply with ONLY this JSON object on a single line: '
            '{"suggestions": ["...", "...", "..."]}'
        )
        # Reuse the last few exchanges so the model has context, but cap size.
        tail = prior_messages[-6:] if len(prior_messages) > 6 else prior_messages[:]
        # Append the latest assistant text (we already streamed it but it's
        # not yet in prior_messages on this iteration).
        if latest_assistant_text:
            tail = tail + [{"role": "assistant", "content": latest_assistant_text}]
        suggestion_messages: List[Dict[str, Any]] = [
            {"role": "system", "content": instruction},
            *tail,
        ]

        text = ""
        try:
            async for ev in provider.stream_chat(suggestion_messages, []):
                if isinstance(ev, TextDelta):
                    text += ev.text
                elif isinstance(ev, Stop):
                    break
                elif isinstance(ev, ErrorEvent):
                    return []
        except Exception:  # noqa: BLE001
            return []

        return _parse_suggestions(text)

    async def _execute_tool_in_thread(self, name: str, args: Dict[str, Any], chat_id: int) -> Dict[str, Any]:
        async def _run() -> Dict[str, Any]:
            db = SessionLocal()
            try:
                ctx = ToolContext(db=db, chat_id=chat_id)
                return await execute_tool(name, args, ctx)
            finally:
                db.close()
        return await _run()

    async def _record_tool_result(
        self,
        chat_id: int,
        tool_call_id: str,
        tool_use_msg_id: int,
        status: str,
        envelope: Dict[str, Any],
    ) -> None:
        await run_in_threadpool(self._update_message, tool_use_msg_id, {"status": status, "tool_result": envelope})
        await run_in_threadpool(
            self._append_message,
            chat_id,
            role="tool_result",
            tool_call_id=tool_call_id,
            tool_name=None,
            tool_result=envelope,
            status="complete",
        )


@dataclass
class _CompactMessage:
    """Lightweight stand-in for a ``ChatMessage`` row, used after compaction.

    Mirrors the attributes the message-builder reads, so callers can treat
    compacted and live rows uniformly.
    """
    id: int
    role: str
    content: Optional[str]
    tool_call_id: Optional[str]
    tool_name: Optional[str]
    tool_args: Optional[Any]
    tool_result: Optional[Any]
    parent_message_id: Optional[int] = None
    status: str = "complete"


def _estimate_size(messages: List[Any]) -> int:
    total = 0
    for m in messages:
        if getattr(m, "content", None):
            total += len(m.content)
        if getattr(m, "tool_args", None):
            try:
                total += len(json.dumps(m.tool_args, default=str))
            except (TypeError, ValueError):
                total += 256
        if getattr(m, "tool_result", None):
            try:
                total += len(json.dumps(m.tool_result, default=str))
            except (TypeError, ValueError):
                total += 256
    return total


def _compact_history(messages: List[Any]) -> List[Any]:
    """Drop the bulk of older tool payloads when the prompt would be huge.

    Keeps the most recent ``COMPACT_KEEP_RECENT`` messages verbatim. For older
    ``tool_use`` / ``tool_result`` rows, replaces the payload with a short
    summary so the model still sees the conversational structure but doesn't
    spend tokens on stale data.
    """
    if _estimate_size(messages) <= COMPACT_BUDGET_CHARS or len(messages) <= COMPACT_KEEP_RECENT:
        return messages

    cutoff = len(messages) - COMPACT_KEEP_RECENT
    head = messages[:cutoff]
    tail = messages[cutoff:]

    compacted_head: List[Any] = []
    for m in head:
        if m.role == "tool_use":
            args_summary = _summarize_args(m.tool_args)
            compacted_head.append(_CompactMessage(
                id=m.id,
                role="tool_use",
                content=None,
                tool_call_id=m.tool_call_id,
                tool_name=m.tool_name,
                tool_args={"_summary": args_summary},
                tool_result=None,
                parent_message_id=m.parent_message_id,
                status=m.status,
            ))
        elif m.role == "tool_result":
            compacted_head.append(_CompactMessage(
                id=m.id,
                role="tool_result",
                content=None,
                tool_call_id=m.tool_call_id,
                tool_name=m.tool_name,
                tool_args=None,
                tool_result={"_summary": "[result elided for context compaction]"},
                parent_message_id=m.parent_message_id,
                status=m.status,
            ))
        elif m.role == "assistant" and m.content and len(m.content) > 1000:
            compacted_head.append(_CompactMessage(
                id=m.id,
                role="assistant",
                content=m.content[:800] + "…[truncated]",
                tool_call_id=None,
                tool_name=None,
                tool_args=None,
                tool_result=None,
                parent_message_id=m.parent_message_id,
                status=m.status,
            ))
        else:
            compacted_head.append(m)

    return compacted_head + tail


def _summarize_args(args: Any) -> str:
    if args is None:
        return ""
    try:
        encoded = json.dumps(args, default=str)
    except (TypeError, ValueError):
        return str(args)[:80]
    return encoded[:80] + ("…" if len(encoded) > 80 else "")


_TIER_LABELS = {
    "long_term": "Long-term notes (durable preferences, recurring routines, traits)",
    "mid_term": "Mid-term notes (current focus, ongoing themes, last few weeks)",
    "short_term": "Short-term notes (today / very recent — likely to expire soon)",
    "general": "General notes",
}
_TIER_ORDER = ("long_term", "mid_term", "short_term", "general")


def _format_ai_memories(memories: List[Any]) -> str:
    """Render ai_memories grouped by tier with timestamps for the system prompt.

    Tier order: long → mid → short → general — this puts durable facts first so
    the model anchors on stable preferences, then sees recent context near the
    bottom. Each entry is rendered as ``- (key) value [recorded YYYY-MM-DD HH:MM]``.
    """
    by_tier: Dict[str, List[Any]] = {t: [] for t in _TIER_ORDER}
    for m in memories:
        tier = (getattr(m, "tier", None) or "general")
        if tier not in by_tier:
            tier = "general"
        by_tier[tier].append(m)

    blocks: List[str] = []
    for tier in _TIER_ORDER:
        rows = by_tier[tier]
        if not rows:
            continue
        lines = [_TIER_LABELS[tier] + ":"]
        for r in rows:
            stamp = ""
            ts = getattr(r, "updated_at", None)
            if ts is not None:
                try:
                    if hasattr(ts, "strftime"):
                        stamp = f" [recorded {ts.strftime('%Y-%m-%d %H:%M')}]"
                except Exception:
                    pass
            cat = getattr(r, "category", None)
            cat_part = f"[{cat}] " if cat and cat != "general" else ""
            lines.append(f"- {cat_part}{r.key}: {r.value}{stamp}")
        blocks.append("\n".join(lines))

    if not blocks:
        return ""
    header = "Memories you (the assistant) wrote earlier — refer to them when relevant:"
    return header + "\n\n" + "\n\n".join(blocks)


def _parse_suggestions(text: str) -> List[str]:
    """Best-effort parser for ``{"suggestions": [...]}`` JSON.

    Strips markdown fences, finds the outermost ``{...}``, parses, and
    returns up to 3 trimmed strings shorter than 80 chars each.
    """
    if not text:
        return []
    cleaned = text.strip()
    if cleaned.startswith("```"):
        cleaned = cleaned.strip("`")
        if cleaned.lower().startswith("json"):
            cleaned = cleaned[4:].lstrip()
    # Locate the JSON object even if the model wrapped it in prose.
    start = cleaned.find("{")
    end = cleaned.rfind("}")
    if start == -1 or end == -1 or end <= start:
        return []
    try:
        data = json.loads(cleaned[start : end + 1])
    except json.JSONDecodeError:
        return []
    raw = data.get("suggestions") if isinstance(data, dict) else None
    if not isinstance(raw, list):
        return []
    out: List[str] = []
    for item in raw:
        if isinstance(item, str):
            stripped = item.strip()
            if stripped:
                out.append(stripped[:80])
        if len(out) >= 3:
            break
    return out


def _current_time_context() -> str:
    """One-line current-time advisory for the system prompt.

    Includes day name, ISO date, local time, and the IANA-ish tz name. We
    explicitly tell the model to use the user's local wall-clock when calling
    tools — the planner stores naive local datetimes everywhere.
    """
    now = datetime.now().astimezone()
    iso_local = now.replace(microsecond=0).isoformat()
    offset = now.strftime("%z")
    if len(offset) == 5:
        offset = offset[:3] + ":" + offset[3:]
    tz_name = now.tzname() or "local"
    return (
        f"Current local date/time: {now.strftime('%A, %B %d, %Y, %H:%M')} "
        f"(ISO: {iso_local}, timezone: {tz_name} {offset}). "
        "When you call tools that take datetimes, send the user's local wall-clock value "
        "without a 'Z' suffix or UTC offset — the planner stores everything as local time."
    )


def _format_user_timestamp(value) -> Optional[str]:
    """Format a chat-message ``created_at`` timestamp for inclusion in user content."""
    if value is None:
        return None
    try:
        if isinstance(value, str):
            ts = datetime.fromisoformat(value.replace("Z", "+00:00"))
        else:
            ts = value
        if getattr(ts, "tzinfo", None) is not None:
            ts = ts.astimezone().replace(tzinfo=None)
        return ts.strftime("%Y-%m-%d %H:%M")
    except (ValueError, TypeError):
        return None


def _resolve_tool_args(meta: Dict[str, Any]) -> Dict[str, Any]:
    """Pick the best dict-shaped args from a streamed tool-call's metadata."""
    if meta.get("parsed_args") is not None:
        return meta["parsed_args"]
    if meta.get("parse_error"):
        return {}
    buf = meta.get("args_buffer", "")
    if not buf:
        return {}
    try:
        return json.loads(buf)
    except json.JSONDecodeError:
        return {}


def _build_extra_headers(config: Dict[str, Any]) -> Dict[str, str]:
    base = {}
    if "openrouter" in (config.get("base_url") or "").lower():
        # OpenRouter encourages an HTTP-Referer + X-Title for analytics; harmless if absent.
        base["HTTP-Referer"] = "http://localhost"
        base["X-Title"] = "Ubuntu-Planner"
    return base


def _effective_permission_for(
    tool_name: str,
    chat_overrides: Optional[Dict[str, str]],
    global_overrides: Optional[Dict[str, str]],
) -> str:
    from app.services.ai.tools.registry import all_tools, DEFAULT_TIER_LEVELS
    for t in all_tools():
        if t.name == tool_name:
            return resolve_permission(t, chat_overrides, global_overrides)
    return "deny"


def _format_tool_result_for_model(payload: Any) -> str:
    if payload is None:
        return ""
    try:
        return json.dumps(payload, default=str)
    except (TypeError, ValueError):
        return str(payload)


def _serialize_message(msg) -> Dict[str, Any]:
    return {
        "id": msg.id,
        "chat_id": msg.chat_id,
        "role": msg.role,
        "content": msg.content,
        "tool_call_id": msg.tool_call_id,
        "tool_name": msg.tool_name,
        "tool_args": msg.tool_args,
        "tool_result": msg.tool_result,
        "status": msg.status,
        "parent_message_id": msg.parent_message_id,
        "created_at": msg.created_at.isoformat() if msg.created_at else None,
    }
