"""Launcher schemas."""

from __future__ import annotations

from pydantic import BaseModel


class LaunchTemplate(BaseModel):
    name: str
    agent_type: str = "claude_code"
    command: str
    working_directory: str | None = None
    env_vars: dict[str, str] | None = None
    prompt_file: str | None = None
    worktree_strategy: str | None = None


class LaunchRequest(BaseModel):
    ticket_identifier: str
    template_name: str = "default"


class LaunchResponse(BaseModel):
    session_id: str | None
    pid: int | None
    message: str
