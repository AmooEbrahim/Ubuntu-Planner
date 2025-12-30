from sqlalchemy import Column, String, JSON, TIMESTAMP
from sqlalchemy.sql import func
from app.core.database import Base


class Setting(Base):
    """Settings model for storing application configuration."""

    __tablename__ = "settings"

    key_name = Column(String(100), primary_key=True)
    value_json = Column(JSON, nullable=False)
    updated_at = Column(TIMESTAMP, server_default=func.now(), onupdate=func.now())
