"""Lease schemas."""

from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel


class LeaseAcquireRequest(BaseModel):
    resource_key: str = "shared-dev"
    session_id: str
    ticket_identifier: str | None = None
    commit_sha: str | None = None
    ttl_seconds: int | None = None
    metadata_json: str | None = None


class LeaseHeartbeatRequest(BaseModel):
    resource_key: str = "shared-dev"
    session_id: str
    extend_seconds: int | None = None


class LeaseReleaseRequest(BaseModel):
    resource_key: str = "shared-dev"
    session_id: str
    release_reason: str | None = None


class LeaseResponse(BaseModel):
    id: str
    resource_key: str
    session_id: str
    ticket_identifier: str | None
    commit_sha: str | None
    state: str
    acquired_at: datetime
    expires_at: datetime
    heartbeat_at: datetime
    released_at: datetime | None
    release_reason: str | None
    metadata_json: str | None

    model_config = {"from_attributes": True}
