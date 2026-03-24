"""Session management service."""

from __future__ import annotations

from datetime import datetime, timezone

from fastapi import HTTPException
from sqlalchemy.orm import Session

from app.models.session import SessionModel
from app.models.status_update import StatusUpdate
from app.schemas.session import SessionRegister, SessionStatusUpdate
from app.services.event_service import log_event

VALID_STATUSES = {
    "idle", "starting", "local_dev", "blocked",
    "shared_env_enqueued", "shared_env_lease_acquired",
    "shared_env_deploy_running", "shared_env_deploy_complete",
    "shared_env_verification", "shared_env_released",
    "completed", "failed", "cancelled",
}


def register_session(db: Session, data: SessionRegister) -> SessionModel:
    session = SessionModel(
        agent_type=data.agent_type,
        display_name=data.display_name,
        pid=data.pid,
        host=data.host,
        worktree_path=data.worktree_path,
        branch_name=data.branch_name,
        repo_path=data.repo_path,
        ticket_id=data.ticket_id,
        status=data.status,
        metadata_json=data.metadata_json,
    )
    db.add(session)
    log_event(db, "session_registered", f"Session {session.display_name or session.id} registered",
              session_id=session.id, ticket_identifier=data.ticket_id)
    db.commit()
    db.refresh(session)
    return session


def heartbeat_session(db: Session, session_id: str) -> SessionModel:
    session = db.query(SessionModel).filter(SessionModel.id == session_id).first()
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
    session.last_seen_at = datetime.now(timezone.utc)
    db.commit()
    db.refresh(session)
    return session


def update_session_status(db: Session, session_id: str, data: SessionStatusUpdate) -> SessionModel:
    session = db.query(SessionModel).filter(SessionModel.id == session_id).first()
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
    if data.status not in VALID_STATUSES:
        raise HTTPException(status_code=400, detail=f"Invalid status: {data.status}")

    old_status = session.status
    session.status = data.status
    session.last_seen_at = datetime.now(timezone.utc)

    status_update = StatusUpdate(
        session_id=session_id,
        status=data.status,
        summary=data.summary,
    )
    db.add(status_update)
    log_event(db, "status_changed", f"{old_status} -> {data.status}: {data.summary or ''}",
              session_id=session_id)
    db.commit()
    db.refresh(session)
    return session


def end_session(db: Session, session_id: str) -> SessionModel:
    session = db.query(SessionModel).filter(SessionModel.id == session_id).first()
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
    session.ended_at = datetime.now(timezone.utc)
    session.status = "completed"
    log_event(db, "session_ended", f"Session {session.display_name or session.id} ended",
              session_id=session_id)
    db.commit()
    db.refresh(session)
    return session


def list_sessions(db: Session, active_only: bool = False) -> list[SessionModel]:
    q = db.query(SessionModel)
    if active_only:
        q = q.filter(SessionModel.ended_at.is_(None))
    return q.order_by(SessionModel.started_at.desc()).all()


def get_session(db: Session, session_id: str) -> SessionModel:
    session = db.query(SessionModel).filter(SessionModel.id == session_id).first()
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
    return session
