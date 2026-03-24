"""Queue management service."""

from __future__ import annotations

from datetime import datetime, timezone

from fastapi import HTTPException
from sqlalchemy.orm import Session

from app.models.queue_entry import QueueEntry
from app.models.resource import Resource
from app.schemas.queue import QueueEnqueueRequest
from app.services.event_service import log_event


def enqueue(db: Session, data: QueueEnqueueRequest) -> QueueEntry:
    resource = db.query(Resource).filter(Resource.key == data.resource_key).first()
    if not resource:
        raise HTTPException(status_code=404, detail=f"Resource '{data.resource_key}' not found")

    existing = (
        db.query(QueueEntry)
        .filter(
            QueueEntry.resource_key == data.resource_key,
            QueueEntry.session_id == data.session_id,
            QueueEntry.state == "queued",
        )
        .first()
    )
    if existing:
        raise HTTPException(status_code=409, detail="Session is already queued for this resource")

    entry = QueueEntry(
        resource_key=data.resource_key,
        session_id=data.session_id,
        ticket_identifier=data.ticket_identifier,
        priority=data.priority,
        metadata_json=data.metadata_json,
    )
    db.add(entry)
    log_event(db, "queue_enqueued", f"Session enqueued for {data.resource_key}",
              session_id=data.session_id, resource_key=data.resource_key,
              ticket_identifier=data.ticket_identifier)
    db.commit()
    db.refresh(entry)
    return entry


def cancel_entry(db: Session, entry_id: str) -> QueueEntry:
    entry = db.query(QueueEntry).filter(QueueEntry.id == entry_id).first()
    if not entry:
        raise HTTPException(status_code=404, detail="Queue entry not found")
    if entry.state != "queued":
        raise HTTPException(status_code=400, detail=f"Cannot cancel entry in state '{entry.state}'")

    entry.state = "cancelled"
    entry.completed_at = datetime.now(timezone.utc)
    log_event(db, "queue_cancelled", f"Queue entry cancelled",
              session_id=entry.session_id, resource_key=entry.resource_key)
    db.commit()
    db.refresh(entry)
    return entry


def list_queue(db: Session, resource_key: str | None = None) -> list[QueueEntry]:
    q = db.query(QueueEntry).filter(QueueEntry.state == "queued")
    if resource_key:
        q = q.filter(QueueEntry.resource_key == resource_key)
    return q.order_by(QueueEntry.priority.desc(), QueueEntry.requested_at.asc()).all()


def list_queue_all(db: Session) -> list[QueueEntry]:
    return (
        db.query(QueueEntry)
        .filter(QueueEntry.state == "queued")
        .order_by(QueueEntry.priority.desc(), QueueEntry.requested_at.asc())
        .all()
    )
