"""Chat service: CRUD over chats, messages, and AI memory."""
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional

from sqlalchemy import desc
from sqlalchemy.orm import Session, selectinload

from app.models.chat import AIMemory, Chat, ChatMessage


# How fresh a memory must be to be eligible for the system prompt, by tier.
# Tunable; the loader strips anything older. The list-tool ignores these
# windows so the AI can still audit / prune older entries when asked.
PROMPT_TIER_WINDOWS: Dict[str, timedelta] = {
    "short_term": timedelta(days=3),
    "mid_term": timedelta(days=60),
    "long_term": timedelta(days=730),
    "general": timedelta(days=30),
}

# Per-tier cap inside the system prompt, so one tier can't crowd out others.
PROMPT_TIER_CAPS: Dict[str, int] = {
    "short_term": 10,
    "mid_term": 15,
    "long_term": 20,
    "general": 10,
}


class ChatService:
    """Service for chat conversations and persistent AI memory."""

    # Hard cap for the audit/list view exposed via the tool + REST endpoint.
    # Generous on purpose — the AI uses it to see what it has and prune.
    AI_MEMORY_CAP = 200

    def __init__(self, db: Session) -> None:
        self.db = db

    # ---------- Chats ----------

    def list_chats(self, include_archived: bool = False) -> List[Chat]:
        q = self.db.query(Chat)
        if not include_archived:
            q = q.filter(Chat.archived.is_(False))
        return q.order_by(desc(Chat.updated_at)).all()

    def get_chat(self, chat_id: int, with_messages: bool = False) -> Optional[Chat]:
        q = self.db.query(Chat)
        if with_messages:
            q = q.options(selectinload(Chat.messages))
        return q.filter(Chat.id == chat_id).first()

    def create_chat(self, title: Optional[str] = None) -> Chat:
        chat = Chat(title=title or "New chat")
        self.db.add(chat)
        self.db.commit()
        self.db.refresh(chat)
        return chat

    def update_chat(self, chat_id: int, data: Dict[str, Any]) -> Chat:
        chat = self.db.query(Chat).filter(Chat.id == chat_id).first()
        if chat is None:
            raise ValueError("Chat not found")
        for key in ("title", "archived", "permissions", "system_prompt_override", "model_override"):
            if key in data:
                setattr(chat, key, data[key])
        self.db.commit()
        self.db.refresh(chat)
        return chat

    def delete_chat(self, chat_id: int) -> bool:
        chat = self.db.query(Chat).filter(Chat.id == chat_id).first()
        if chat is None:
            return False
        self.db.delete(chat)
        self.db.commit()
        return True

    def touch(self, chat_id: int) -> None:
        """Bump ``updated_at`` so the chat sorts to the top of the list."""
        from sqlalchemy import update
        self.db.execute(
            update(Chat).where(Chat.id == chat_id).values(updated_at=Chat.updated_at)
        )
        self.db.commit()

    # ---------- Messages ----------

    def list_messages(
        self,
        chat_id: int,
        since_id: Optional[int] = None,
    ) -> List[ChatMessage]:
        q = self.db.query(ChatMessage).filter(ChatMessage.chat_id == chat_id)
        if since_id is not None:
            q = q.filter(ChatMessage.id > since_id)
        return q.order_by(ChatMessage.created_at.asc(), ChatMessage.id.asc()).all()

    def get_message(self, message_id: int) -> Optional[ChatMessage]:
        return self.db.query(ChatMessage).filter(ChatMessage.id == message_id).first()

    def append_message(self, chat_id: int, **fields: Any) -> ChatMessage:
        msg = ChatMessage(chat_id=chat_id, **fields)
        self.db.add(msg)
        self.db.commit()
        self.db.refresh(msg)
        return msg

    def update_message(self, message_id: int, fields: Dict[str, Any]) -> ChatMessage:
        msg = self.db.query(ChatMessage).filter(ChatMessage.id == message_id).first()
        if msg is None:
            raise ValueError("Message not found")
        for key, value in fields.items():
            if hasattr(msg, key):
                setattr(msg, key, value)
        self.db.commit()
        self.db.refresh(msg)
        return msg

    def has_pending_tool_calls(self, chat_id: int) -> bool:
        return (
            self.db.query(ChatMessage)
            .filter(
                ChatMessage.chat_id == chat_id,
                ChatMessage.status == "pending",
                ChatMessage.role == "tool_use",
            )
            .first()
            is not None
        )

    def get_pending_tool_calls(self, chat_id: int) -> List[ChatMessage]:
        return (
            self.db.query(ChatMessage)
            .filter(
                ChatMessage.chat_id == chat_id,
                ChatMessage.status == "pending",
                ChatMessage.role == "tool_use",
            )
            .order_by(ChatMessage.created_at.asc())
            .all()
        )

    def resolve_tool_call(
        self,
        chat_id: int,
        tool_call_id: str,
        new_status: str,
        tool_result: Optional[dict] = None,
    ) -> int:
        """Atomically transition a pending tool call to a new terminal status.

        Returns the number of rows updated (0 if already resolved or absent).
        Uses ``UPDATE ... WHERE status='pending'`` to prevent races.
        """
        from sqlalchemy import update
        stmt = (
            update(ChatMessage)
            .where(
                ChatMessage.chat_id == chat_id,
                ChatMessage.tool_call_id == tool_call_id,
                ChatMessage.status == "pending",
                ChatMessage.role == "tool_use",
            )
            .values(status=new_status)
        )
        result = self.db.execute(stmt)
        self.db.commit()
        return result.rowcount or 0

    # ---------- AI memory ----------

    def list_ai_memories(self) -> List[AIMemory]:
        """All memories, newest first, up to ``AI_MEMORY_CAP``.

        Used by the ``list_ai_memories`` tool and the REST endpoint — does
        NOT apply the per-tier expiry windows, so the AI / user can still
        see "stale" entries to audit or delete them.
        """
        return (
            self.db.query(AIMemory)
            .order_by(desc(AIMemory.updated_at))
            .limit(self.AI_MEMORY_CAP)
            .all()
        )

    def list_ai_memories_for_prompt(self) -> List[AIMemory]:
        """Memories eligible for system-prompt injection.

        Per-tier windows + per-tier caps; rows older than their tier's window
        are filtered out so dead routines don't anchor the model forever.
        Update of a row resets its window (because ``updated_at`` is bumped).

        Returned rows are flat (caller groups by tier for rendering) and
        sorted within tier by recency.
        """
        now = datetime.now()
        out: List[AIMemory] = []
        for tier, window in PROMPT_TIER_WINDOWS.items():
            cap = PROMPT_TIER_CAPS.get(tier, 10)
            cutoff = now - window
            rows = (
                self.db.query(AIMemory)
                .filter(AIMemory.tier == tier, AIMemory.updated_at >= cutoff)
                .order_by(desc(AIMemory.updated_at))
                .limit(cap)
                .all()
            )
            out.extend(rows)
        return out

    def upsert_ai_memory(
        self,
        category: str,
        key: str,
        value: str,
        tier: str = "general",
    ) -> AIMemory:
        existing = (
            self.db.query(AIMemory)
            .filter(AIMemory.category == category, AIMemory.key == key)
            .first()
        )
        if existing is None:
            existing = AIMemory(category=category, key=key, value=value, tier=tier)
            self.db.add(existing)
        else:
            existing.value = value
            existing.tier = tier
        self.db.commit()
        self.db.refresh(existing)
        return existing

    def delete_ai_memory(self, category: str, key: str) -> bool:
        existing = (
            self.db.query(AIMemory)
            .filter(AIMemory.category == category, AIMemory.key == key)
            .first()
        )
        if existing is None:
            return False
        self.db.delete(existing)
        self.db.commit()
        return True
