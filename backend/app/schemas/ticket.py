"""Ticket schemas."""

from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel


class TicketCreate(BaseModel):
    identifier: str
    title: str
    description: str | None = None
    state: str = "open"
    priority: int | None = None
    assignee: str | None = None
    labels_json: str | None = None
    url: str | None = None
    source: str = "manual"
    external_id: str | None = None
    metadata_json: str | None = None


class TicketResponse(BaseModel):
    id: str
    external_id: str | None
    identifier: str
    title: str
    description: str | None
    state: str
    priority: int | None
    assignee: str | None
    labels_json: str | None
    url: str | None
    source: str
    synced_at: datetime
    metadata_json: str | None

    model_config = {"from_attributes": True}
