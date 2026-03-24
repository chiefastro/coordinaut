"""Session schemas."""

from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel, Field


class SessionRegister(BaseModel):
    agent_type: str = "claude_code"
    display_name: str = ""
    pid: int | None = None
    host: str = "localhost"
    worktree_path: str | None = None
    branch_name: str | None = None
    repo_path: str | None = None
    ticket_id: str | None = None
    status: str = "idle"
    metadata_json: str | None = None


class SessionStatusUpdate(BaseModel):
    status: str
    summary: str | None = None


class SessionResponse(BaseModel):
    id: str
    agent_type: str
    display_name: str
    pid: int | None
    host: str
    worktree_path: str | None
    branch_name: str | None
    repo_path: str | None
    ticket_id: str | None
    status: str
    started_at: datetime
    last_seen_at: datetime
    ended_at: datetime | None
    metadata_json: str | None

    model_config = {"from_attributes": True}
