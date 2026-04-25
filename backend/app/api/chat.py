"""Chat API: CRUD, streaming SSE, tool-call decisions, cancel/resume."""
import json
from typing import AsyncIterator, List

from fastapi import APIRouter, Depends, HTTPException, Query
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.schemas.chat import (
    AIMemoryResponse,
    AIMemoryUpsert,
    ChatCreate,
    ChatDetail,
    ChatMessageResponse,
    ChatSummary,
    ChatUpdate,
    ToolDecisionPayload,
    UserMessageCreate,
)
from app.services.ai.agent import (
    AgentRunner,
    StreamEvent,
    cancel_turn,
    is_turn_active,
)
from app.services.chat_service import ChatService


router = APIRouter(prefix="/api/chat", tags=["chat"])


def get_service(db: Session = Depends(get_db)) -> ChatService:
    return ChatService(db)


@router.get("/", response_model=List[ChatSummary])
async def list_chats(
    include_archived: bool = Query(False),
    service: ChatService = Depends(get_service),
):
    return service.list_chats(include_archived=include_archived)


@router.post("/", response_model=ChatDetail, status_code=201)
async def create_chat(data: ChatCreate, service: ChatService = Depends(get_service)):
    chat = service.create_chat(title=data.title)
    return _detail(chat, messages=[])


@router.get("/{chat_id}", response_model=ChatDetail)
async def get_chat(chat_id: int, service: ChatService = Depends(get_service)):
    chat = service.get_chat(chat_id, with_messages=True)
    if chat is None:
        raise HTTPException(status_code=404, detail="Chat not found")
    return _detail(chat, messages=chat.messages)


@router.patch("/{chat_id}", response_model=ChatDetail)
async def update_chat(
    chat_id: int, data: ChatUpdate, service: ChatService = Depends(get_service)
):
    try:
        chat = service.update_chat(chat_id, data.model_dump(exclude_unset=True))
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc))
    chat = service.get_chat(chat_id, with_messages=True)
    return _detail(chat, messages=chat.messages)


@router.delete("/{chat_id}", status_code=204)
async def delete_chat(chat_id: int, service: ChatService = Depends(get_service)):
    if not service.delete_chat(chat_id):
        raise HTTPException(status_code=404, detail="Chat not found")


@router.get("/{chat_id}/messages", response_model=List[ChatMessageResponse])
async def list_messages(
    chat_id: int,
    since: int | None = Query(None, description="Only return messages with id > since"),
    service: ChatService = Depends(get_service),
):
    chat = service.get_chat(chat_id)
    if chat is None:
        raise HTTPException(status_code=404, detail="Chat not found")
    return service.list_messages(chat_id, since_id=since)


# --------- Streaming + tool decisions ---------


def _sse_format(event: StreamEvent) -> bytes:
    """Encode one SSE event."""
    payload = json.dumps(event.data, default=str)
    return f"event: {event.type}\ndata: {payload}\n\n".encode("utf-8")


async def _sse_stream(events: AsyncIterator[StreamEvent]) -> AsyncIterator[bytes]:
    yield b": stream-open\n\n"
    async for ev in events:
        yield _sse_format(ev)


def _streaming_response(events: AsyncIterator[StreamEvent]) -> StreamingResponse:
    return StreamingResponse(
        _sse_stream(events),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no",
        },
    )


@router.post("/{chat_id}/messages")
async def post_message(
    chat_id: int,
    data: UserMessageCreate,
    service: ChatService = Depends(get_service),
):
    """Send a user message; return an SSE stream of the assistant's turn."""
    chat = service.get_chat(chat_id)
    if chat is None:
        raise HTTPException(status_code=404, detail="Chat not found")
    if is_turn_active(chat_id):
        raise HTTPException(status_code=409, detail="A turn is already streaming for this chat.")
    if service.has_pending_tool_calls(chat_id):
        raise HTTPException(
            status_code=409,
            detail="A tool call is awaiting your decision. Approve or deny it before sending another message.",
        )

    runner = AgentRunner()
    events = runner.stream_turn(chat_id, data.content)
    return _streaming_response(events)


@router.post("/{chat_id}/cancel", status_code=204)
async def cancel(chat_id: int):
    """Cancel a running turn. No-op if nothing is streaming."""
    cancel_turn(chat_id)


@router.post("/{chat_id}/resume")
async def resume(
    chat_id: int,
    service: ChatService = Depends(get_service),
):
    """Resume the loop after every pending tool call has been resolved."""
    chat = service.get_chat(chat_id)
    if chat is None:
        raise HTTPException(status_code=404, detail="Chat not found")
    if service.has_pending_tool_calls(chat_id):
        raise HTTPException(
            status_code=400,
            detail="Cannot resume — at least one tool call is still pending.",
        )
    if is_turn_active(chat_id):
        raise HTTPException(status_code=409, detail="A turn is already streaming for this chat.")

    runner = AgentRunner()
    events = runner.stream_turn(chat_id, user_content=None, resume=True)
    return _streaming_response(events)


@router.post("/{chat_id}/tool-calls/{tool_call_id}/decision")
async def tool_decision(
    chat_id: int,
    tool_call_id: str,
    data: ToolDecisionPayload,
    service: ChatService = Depends(get_service),
):
    """Approve or deny a pending tool call.

    Approval transitions the row to ``executing`` so a follow-up ``/resume``
    can pick it up and run the tool. Denial records a synthetic denial result
    so the agent can read it on resume.
    """
    chat = service.get_chat(chat_id)
    if chat is None:
        raise HTTPException(status_code=404, detail="Chat not found")

    pending_rows = service.get_pending_tool_calls(chat_id)
    target = next((r for r in pending_rows if r.tool_call_id == tool_call_id), None)
    if target is None:
        raise HTTPException(status_code=404, detail="Pending tool call not found.")

    if data.decision == "approve":
        # Execute now, synchronously. The model sees the result on resume.
        from app.services.ai.tools.registry import (
            ToolContext,
            execute_tool,
            truncate_result,
        )
        ctx = ToolContext(db=service.db, chat_id=chat_id)
        envelope = await execute_tool(target.tool_name, target.tool_args or {}, ctx)
        envelope = truncate_result(envelope, max_bytes=8192)
        status = "complete" if envelope.get("ok") else "error"
        rows = service.resolve_tool_call(chat_id, tool_call_id, status)
        if rows == 0:
            raise HTTPException(status_code=409, detail="Tool call already resolved.")
        service.update_message(target.id, {"tool_result": envelope})
        service.append_message(
            chat_id,
            role="tool_result",
            tool_call_id=tool_call_id,
            tool_result=envelope,
            status="complete",
        )
        return {"status": status, "result": envelope}

    # decision == "deny"
    rows = service.resolve_tool_call(chat_id, tool_call_id, "denied")
    if rows == 0:
        raise HTTPException(status_code=409, detail="Tool call already resolved.")
    envelope = {"ok": False, "error": "User denied this tool call.", "type": "user_denied"}
    service.update_message(target.id, {"tool_result": envelope})
    service.append_message(
        chat_id,
        role="tool_result",
        tool_call_id=tool_call_id,
        tool_result=envelope,
        status="complete",
    )
    return {"status": "denied", "result": envelope}


@router.get("/{chat_id}/stream")
async def stream_reattach(
    chat_id: int,
    since: int | None = Query(None, description="Only emit messages newer than this id."),
    service: ChatService = Depends(get_service),
):
    """Reattach to an in-flight chat turn (Phase 7).

    For now, return a one-shot snapshot of any messages newer than ``since``
    so the client can catch up after a reload. True live SSE reattach can
    layer on top of this without changing the URL.
    """
    chat = service.get_chat(chat_id)
    if chat is None:
        raise HTTPException(status_code=404, detail="Chat not found")
    rows = service.list_messages(chat_id, since_id=since)
    return [ChatMessageResponse.model_validate(r) for r in rows]


# --------- AI memory (separate sub-router for clarity) ---------

memory_router = APIRouter(prefix="/api/ai-memory", tags=["ai-memory"])


@memory_router.get("/", response_model=List[AIMemoryResponse])
async def list_memories(service: ChatService = Depends(get_service)):
    return service.list_ai_memories()


@memory_router.put("/", response_model=AIMemoryResponse)
async def upsert_memory(data: AIMemoryUpsert, service: ChatService = Depends(get_service)):
    return service.upsert_ai_memory(data.category, data.key, data.value, data.tier)


@memory_router.delete("/", status_code=204)
async def delete_memory(
    category: str = Query("general"),
    key: str = Query(...),
    service: ChatService = Depends(get_service),
):
    if not service.delete_ai_memory(category, key):
        raise HTTPException(status_code=404, detail="AI memory not found")


def _detail(chat, messages) -> ChatDetail:
    return ChatDetail(
        id=chat.id,
        title=chat.title,
        archived=chat.archived,
        created_at=chat.created_at,
        updated_at=chat.updated_at,
        permissions=chat.permissions,
        system_prompt_override=chat.system_prompt_override,
        model_override=chat.model_override,
        messages=[ChatMessageResponse.model_validate(m) for m in messages],
    )
