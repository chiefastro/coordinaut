"""Agent launcher service."""

from __future__ import annotations

import json
import os
import subprocess
from pathlib import Path

from fastapi import HTTPException, Depends
from sqlalchemy.orm import Session

from app.config import settings
from app.models.ticket import Ticket
from app.schemas.launcher import LaunchTemplate, LaunchRequest, LaunchResponse
from app.services.event_service import log_event

DEFAULT_TEMPLATES = {
    "default": LaunchTemplate(
        name="default",
        agent_type="claude_code",
        command='claude --prompt "Work on ticket {ticket_identifier}: {ticket_title}"',
        working_directory=None,
        env_vars=None,
        prompt_file=None,
        worktree_strategy=None,
    ),
}


def get_templates() -> dict[str, LaunchTemplate]:
    """Load launch templates from config file or return defaults."""
    config_path = settings.launcher_config_path
    if config_path and Path(config_path).exists():
        try:
            with open(config_path) as f:
                data = json.load(f)
            return {
                name: LaunchTemplate(**tmpl)
                for name, tmpl in data.get("templates", {}).items()
            }
        except Exception:
            pass
    return DEFAULT_TEMPLATES


def launch_agent(db: Session, request: LaunchRequest) -> LaunchResponse:
    templates = get_templates()
    template = templates.get(request.template_name)
    if not template:
        raise HTTPException(status_code=404, detail=f"Template '{request.template_name}' not found")

    ticket = db.query(Ticket).filter(Ticket.identifier == request.ticket_identifier).first()
    if not ticket:
        raise HTTPException(status_code=404, detail=f"Ticket '{request.ticket_identifier}' not found")

    # Substitute variables in command
    cmd = template.command.format(
        ticket_identifier=ticket.identifier,
        ticket_title=ticket.title,
        ticket_description=ticket.description or "",
        ticket_url=ticket.url or "",
    )

    env = os.environ.copy()
    if template.env_vars:
        env.update(template.env_vars)
    env["COORDINAUT_TICKET"] = ticket.identifier
    env["COORDINAUT_TICKET_TITLE"] = ticket.title

    cwd = template.working_directory or os.getcwd()

    try:
        proc = subprocess.Popen(
            cmd,
            shell=True,
            cwd=cwd,
            env=env,
            start_new_session=True,
        )
        log_event(
            db, "launcher_started",
            f"Launched agent for {ticket.identifier} with template '{template.name}' (pid={proc.pid})",
            ticket_identifier=ticket.identifier,
        )
        db.commit()
        return LaunchResponse(
            session_id=None,
            pid=proc.pid,
            message=f"Launched agent for {ticket.identifier} (pid={proc.pid})",
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Launch failed: {e}")
