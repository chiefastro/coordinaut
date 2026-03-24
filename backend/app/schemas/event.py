"""Event schemas."""

from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel


class EventCreate(BaseModel):
    session_id: str | None = None
    ticket_identifier: str | None = None
    resource_key: str | None = None
    event_type: str
    message: str = ""
    payload_json: str | None = None


class EventResponse(BaseModel):
    id: str
    timestamp: datetime
    session_id: str | None
    ticket_identifier: str | None
    resource_key: str | None
    event_type: str
    message: str
    payload_json: str | None

    model_config = {"from_attributes": True}
