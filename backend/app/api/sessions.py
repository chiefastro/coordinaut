"""Session API endpoints."""

from __future__ import annotations

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.db.engine import get_db
from app.schemas.session import SessionRegister, SessionStatusUpdate, SessionResponse
from app.services import session_service

router = APIRouter(prefix="/sessions", tags=["sessions"])


@router.post("/register", response_model=SessionResponse)
def register_session(data: SessionRegister, db: Session = Depends(get_db)):
    return session_service.register_session(db, data)


@router.post("/{session_id}/heartbeat", response_model=SessionResponse)
def heartbeat_session(session_id: str, db: Session = Depends(get_db)):
    return session_service.heartbeat_session(db, session_id)


@router.post("/{session_id}/status", response_model=SessionResponse)
def update_status(session_id: str, data: SessionStatusUpdate, db: Session = Depends(get_db)):
    return session_service.update_session_status(db, session_id, data)


@router.post("/{session_id}/end", response_model=SessionResponse)
def end_session(session_id: str, db: Session = Depends(get_db)):
    return session_service.end_session(db, session_id)


@router.get("", response_model=list[SessionResponse])
def list_sessions(active_only: bool = False, db: Session = Depends(get_db)):
    return session_service.list_sessions(db, active_only=active_only)


@router.get("/{session_id}", response_model=SessionResponse)
def get_session(session_id: str, db: Session = Depends(get_db)):
    return session_service.get_session(db, session_id)
