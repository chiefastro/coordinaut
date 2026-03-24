"""Message service for shared context."""

from __future__ import annotations

from sqlalchemy.orm import Session

from app.models.message import Message
from app.schemas.message import MessageCreate
from app.services.event_service import log_event


def post_message(db: Session, data: MessageCreate) -> Message:
    msg = Message(
        channel=data.channel,
        author_type=data.author_type,
        author_name=data.author_name,
        session_id=data.session_id,
        ticket_identifier=data.ticket_identifier,
        message=data.message,
        metadata_json=data.metadata_json,
    )
    db.add(msg)
    log_event(db, "message_posted", f"Message in #{data.channel} by {data.author_name}",
              session_id=data.session_id, ticket_identifier=data.ticket_identifier)
    db.commit()
    db.refresh(msg)
    return msg


def list_messages(db: Session, limit: int = 100, channel: str | None = None) -> list[Message]:
    q = db.query(Message)
    if channel:
        q = q.filter(Message.channel == channel)
    return q.order_by(Message.created_at.desc()).limit(limit).all()
