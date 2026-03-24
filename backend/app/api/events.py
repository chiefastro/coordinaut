"""Event API endpoints."""

from __future__ import annotations

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.db.engine import get_db
from app.schemas.event import EventCreate, EventResponse
from app.services import event_service

router = APIRouter(prefix="/events", tags=["events"])


@router.get("", response_model=list[EventResponse])
def list_events(
    limit: int = 50,
    session_id: str | None = None,
    event_type: str | None = None,
    resource_key: str | None = None,
    db: Session = Depends(get_db),
):
    return event_service.list_events(
        db, limit=limit, session_id=session_id, event_type=event_type, resource_key=resource_key
    )


@router.post("", response_model=EventResponse)
def create_event(data: EventCreate, db: Session = Depends(get_db)):
    event = event_service.log_event(
        db,
        event_type=data.event_type,
        message=data.message,
        session_id=data.session_id,
        ticket_identifier=data.ticket_identifier,
        resource_key=data.resource_key,
        payload_json=data.payload_json,
    )
    db.commit()
    return event
