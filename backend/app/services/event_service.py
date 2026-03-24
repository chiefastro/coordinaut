"""Event logging service."""

from __future__ import annotations

from sqlalchemy.orm import Session

from app.models.workflow_event import WorkflowEvent


def log_event(
    db: Session,
    event_type: str,
    message: str = "",
    session_id: str | None = None,
    ticket_identifier: str | None = None,
    resource_key: str | None = None,
    payload_json: str | None = None,
) -> WorkflowEvent:
    event = WorkflowEvent(
        event_type=event_type,
        message=message,
        session_id=session_id,
        ticket_identifier=ticket_identifier,
        resource_key=resource_key,
        payload_json=payload_json,
    )
    db.add(event)
    db.flush()
    return event


def list_events(
    db: Session,
    limit: int = 50,
    session_id: str | None = None,
    event_type: str | None = None,
    resource_key: str | None = None,
) -> list[WorkflowEvent]:
    q = db.query(WorkflowEvent)
    if session_id:
        q = q.filter(WorkflowEvent.session_id == session_id)
    if event_type:
        q = q.filter(WorkflowEvent.event_type == event_type)
    if resource_key:
        q = q.filter(WorkflowEvent.resource_key == resource_key)
    return q.order_by(WorkflowEvent.timestamp.desc()).limit(limit).all()
