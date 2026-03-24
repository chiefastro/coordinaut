"""Message schemas."""

from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel


class MessageCreate(BaseModel):
    channel: str = "common"
    author_type: str = "human"
    author_name: str = ""
    session_id: str | None = None
    ticket_identifier: str | None = None
    message: str
    metadata_json: str | None = None


class MessageResponse(BaseModel):
    id: str
    channel: str
    author_type: str
    author_name: str
    session_id: str | None
    ticket_identifier: str | None
    message: str
    created_at: datetime
    metadata_json: str | None

    model_config = {"from_attributes": True}
