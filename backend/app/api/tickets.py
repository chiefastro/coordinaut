"""Ticket API endpoints."""

from __future__ import annotations

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.db.engine import get_db
from app.schemas.ticket import TicketCreate, TicketResponse
from app.services import ticket_service
from app.integrations.linear import import_linear_tickets, get_linear_teams

router = APIRouter(prefix="/tickets", tags=["tickets"])


@router.get("", response_model=list[TicketResponse])
def list_tickets(db: Session = Depends(get_db)):
    return ticket_service.list_tickets(db)


@router.post("", response_model=TicketResponse)
def create_ticket(data: TicketCreate, db: Session = Depends(get_db)):
    return ticket_service.create_ticket(db, data)


@router.get("/{identifier}", response_model=TicketResponse)
def get_ticket(identifier: str, db: Session = Depends(get_db)):
    return ticket_service.get_ticket(db, identifier)


@router.post("/import/linear", response_model=list[TicketResponse])
def import_from_linear(
    team_id: str = Query(None, description="Linear team ID (auto-discovers if omitted)"),
    db: Session = Depends(get_db),
):
    return import_linear_tickets(db, team_id=team_id)


@router.get("/linear/teams")
def linear_teams():
    return get_linear_teams()
