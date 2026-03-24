"""Message model."""

from __future__ import annotations

from typing import Optional

import uuid
from datetime import datetime, timezone

from sqlalchemy import String, DateTime, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base


class Message(Base):
    __tablename__ = "messages"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    channel: Mapped[str] = mapped_column(String(200), default="common", index=True)
    author_type: Mapped[str] = mapped_column(String(20), default="human")
    author_name: Mapped[str] = mapped_column(String(200), default="")
    session_id: Mapped[Optional[str]] = mapped_column(String(36), nullable=True)
    ticket_identifier: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    message: Mapped[str] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), index=True
    )
    metadata_json: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
