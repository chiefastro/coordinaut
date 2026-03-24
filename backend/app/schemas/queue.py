"""Queue schemas."""

from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel


class QueueEnqueueRequest(BaseModel):
    resource_key: str = "shared-dev"
    session_id: str
    ticket_identifier: str | None = None
    priority: int = 0
    metadata_json: str | None = None


class QueueEntryResponse(BaseModel):
    id: str
    resource_key: str
    session_id: str
    ticket_identifier: str | None
    priority: int
    state: str
    requested_at: datetime
    granted_at: datetime | None
    completed_at: datetime | None
    metadata_json: str | None

    model_config = {"from_attributes": True}
