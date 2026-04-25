"""Chat models: conversations, messages, and cross-chat AI memory."""
from sqlalchemy import (
    Boolean,
    Column,
    Enum,
    ForeignKey,
    Integer,
    JSON,
    String,
    Text,
    TIMESTAMP,
    UniqueConstraint,
    Index,
)
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.core.database import Base


class Chat(Base):
    """A single conversation thread."""

    __tablename__ = "chats"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(255), nullable=False, default="New chat")
    archived = Column(Boolean, nullable=False, default=False, server_default="0")

    permissions = Column(JSON, nullable=True)
    system_prompt_override = Column(Text, nullable=True)
    model_override = Column(String(128), nullable=True)

    created_at = Column(TIMESTAMP, server_default=func.now())
    updated_at = Column(TIMESTAMP, server_default=func.now(), onupdate=func.now())

    messages = relationship(
        "ChatMessage",
        back_populates="chat",
        cascade="all, delete-orphan",
        order_by="ChatMessage.created_at",
    )


class ChatMessage(Base):
    """A single message in a chat — user, assistant, tool_use, or tool_result.

    Tool-call denormalization: a single assistant turn may emit multiple tool
    calls; each tool call gets its own ``tool_use`` row whose
    ``parent_message_id`` points to the assistant text row, plus a matching
    ``tool_result`` row.
    """

    __tablename__ = "chat_messages"
    __table_args__ = (
        # No unique constraint on (chat_id, tool_call_id): a single id appears
        # on both the tool_use row and the matching tool_result row. Race
        # safety on tool-call resolution is handled by the
        # ``UPDATE ... WHERE status='pending'`` rowcount check in
        # :meth:`ChatService.resolve_tool_call`.
        Index("ix_chat_messages_chat_created", "chat_id", "created_at"),
        Index("ix_chat_messages_chat_tool_call", "chat_id", "tool_call_id"),
    )

    id = Column(Integer, primary_key=True, index=True)
    chat_id = Column(Integer, ForeignKey("chats.id", ondelete="CASCADE"), nullable=False)
    parent_message_id = Column(
        Integer,
        ForeignKey("chat_messages.id", ondelete="SET NULL"),
        nullable=True,
    )

    role = Column(
        Enum("system", "user", "assistant", "tool_use", "tool_result", name="chat_message_role"),
        nullable=False,
    )
    content = Column(Text, nullable=True)

    tool_call_id = Column(String(128), nullable=True)
    tool_name = Column(String(64), nullable=True)
    tool_args = Column(JSON, nullable=True)
    tool_result = Column(JSON, nullable=True)

    status = Column(
        Enum(
            "pending",
            "executing",
            "complete",
            "denied",
            "error",
            "cancelled",
            name="chat_message_status",
        ),
        nullable=False,
        default="complete",
        server_default="complete",
    )

    prompt_tokens = Column(Integer, nullable=True)
    completion_tokens = Column(Integer, nullable=True)
    model = Column(String(64), nullable=True)

    # Suggested follow-up replies emitted at the end of an assistant turn.
    # JSON list of short strings, set by ``AgentRunner._generate_suggestions``.
    suggested_replies = Column(JSON, nullable=True)

    created_at = Column(TIMESTAMP, server_default=func.now(), index=True)

    chat = relationship("Chat", back_populates="messages")


class AIMemory(Base):
    """A cross-chat persistent fact the AI can write to and read from.

    Stored as ``(category, key)`` so the AI can group memories thematically.
    Each entry has a ``tier`` — ``short_term`` for ephemeral mood/state,
    ``mid_term`` for current focus across days/weeks, ``long_term`` for
    durable preferences and recurring routines, and ``general`` for misc.
    The total row count is intended to stay small (~50); the loader
    prepends the most-recently-updated entries to the system prompt.
    """

    __tablename__ = "ai_memories"
    __table_args__ = (
        UniqueConstraint("category", "key", name="uq_ai_memories_category_key"),
    )

    id = Column(Integer, primary_key=True, index=True)
    category = Column(String(64), nullable=False, default="general", server_default="general")
    key = Column(String(255), nullable=False)
    value = Column(Text, nullable=False)
    tier = Column(
        Enum("short_term", "mid_term", "long_term", "general", name="ai_memory_tier"),
        nullable=False,
        default="general",
        server_default="general",
    )

    created_at = Column(TIMESTAMP, server_default=func.now())
    updated_at = Column(TIMESTAMP, server_default=func.now(), onupdate=func.now())
