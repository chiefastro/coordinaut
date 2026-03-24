"""Ticket service."""

from __future__ import annotations

from fastapi import HTTPException
from sqlalchemy.orm import Session

from app.models.ticket import Ticket
from app.schemas.ticket import TicketCreate


def create_ticket(db: Session, data: TicketCreate) -> Ticket:
    existing = db.query(Ticket).filter(Ticket.identifier == data.identifier).first()
    if existing:
        # Update existing ticket
        for field in ["title", "description", "state", "priority", "assignee",
                       "labels_json", "url", "source", "external_id", "metadata_json"]:
            val = getattr(data, field)
            if val is not None:
                setattr(existing, field, val)
        db.commit()
        db.refresh(existing)
        return existing

    ticket = Ticket(
        identifier=data.identifier,
        title=data.title,
        description=data.description,
        state=data.state,
        priority=data.priority,
        assignee=data.assignee,
        labels_json=data.labels_json,
        url=data.url,
        source=data.source,
        external_id=data.external_id,
        metadata_json=data.metadata_json,
    )
    db.add(ticket)
    db.commit()
    db.refresh(ticket)
    return ticket


def list_tickets(db: Session) -> list[Ticket]:
    return db.query(Ticket).order_by(Ticket.synced_at.desc()).all()


def get_ticket(db: Session, identifier: str) -> Ticket:
    ticket = db.query(Ticket).filter(Ticket.identifier == identifier).first()
    if not ticket:
        raise HTTPException(status_code=404, detail=f"Ticket '{identifier}' not found")
    return ticket
