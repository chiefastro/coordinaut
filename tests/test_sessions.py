"""Session service tests."""
from __future__ import annotations

from app.schemas.session import SessionRegister, SessionStatusUpdate
from app.services.session_service import (
    register_session, heartbeat_session, update_session_status,
    end_session, list_sessions, get_session,
)


def test_register_session(db):
    data = SessionRegister(agent_type="claude_code", display_name="test-agent")
    session = register_session(db, data)
    assert session.id
    assert session.agent_type == "claude_code"
    assert session.display_name == "test-agent"
    assert session.status == "idle"


def test_heartbeat_session(db):
    data = SessionRegister(display_name="hb-test")
    session = register_session(db, data)
    old_seen = session.last_seen_at
    updated = heartbeat_session(db, session.id)
    assert updated.last_seen_at >= old_seen


def test_update_status(db):
    data = SessionRegister(display_name="status-test")
    session = register_session(db, data)
    updated = update_session_status(db, session.id, SessionStatusUpdate(status="local_dev", summary="working"))
    assert updated.status == "local_dev"


def test_end_session(db):
    data = SessionRegister(display_name="end-test")
    session = register_session(db, data)
    ended = end_session(db, session.id)
    assert ended.ended_at is not None
    assert ended.status == "completed"


def test_list_sessions(db):
    register_session(db, SessionRegister(display_name="a"))
    register_session(db, SessionRegister(display_name="b"))
    sessions = list_sessions(db)
    assert len(sessions) >= 2


def test_list_active_only(db):
    s = register_session(db, SessionRegister(display_name="active-test"))
    end_session(db, s.id)
    register_session(db, SessionRegister(display_name="still-active"))
    active = list_sessions(db, active_only=True)
    names = [s.display_name for s in active]
    assert "still-active" in names
