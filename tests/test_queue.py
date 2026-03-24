"""Queue service tests."""
from __future__ import annotations

import pytest
from fastapi import HTTPException

from app.schemas.session import SessionRegister
from app.schemas.queue import QueueEnqueueRequest
from app.services.session_service import register_session
from app.services.queue_service import enqueue, cancel_entry, list_queue


def _make_session(db, name="test"):
    return register_session(db, SessionRegister(display_name=name))


def test_enqueue(db):
    s = _make_session(db, "queuer")
    entry = enqueue(db, QueueEnqueueRequest(session_id=s.id))
    assert entry.state == "queued"
    assert entry.resource_key == "shared-dev"


def test_queue_order(db):
    s1 = _make_session(db, "first")
    s2 = _make_session(db, "second")
    enqueue(db, QueueEnqueueRequest(session_id=s1.id))
    enqueue(db, QueueEnqueueRequest(session_id=s2.id))
    q = list_queue(db, "shared-dev")
    assert q[0].session_id == s1.id
    assert q[1].session_id == s2.id


def test_priority_ordering(db):
    s1 = _make_session(db, "low")
    s2 = _make_session(db, "high")
    enqueue(db, QueueEnqueueRequest(session_id=s1.id, priority=0))
    enqueue(db, QueueEnqueueRequest(session_id=s2.id, priority=10))
    q = list_queue(db, "shared-dev")
    assert q[0].session_id == s2.id  # higher priority first


def test_cancel(db):
    s = _make_session(db, "canceller")
    entry = enqueue(db, QueueEnqueueRequest(session_id=s.id))
    cancelled = cancel_entry(db, entry.id)
    assert cancelled.state == "cancelled"
    q = list_queue(db, "shared-dev")
    assert len(q) == 0


def test_duplicate_enqueue_fails(db):
    s = _make_session(db, "dup")
    enqueue(db, QueueEnqueueRequest(session_id=s.id))
    with pytest.raises(HTTPException) as exc:
        enqueue(db, QueueEnqueueRequest(session_id=s.id))
    assert exc.value.status_code == 409
