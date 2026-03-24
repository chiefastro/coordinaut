"""Lease service tests — the most critical tests in the app."""
from __future__ import annotations

from datetime import datetime, timezone, timedelta

import pytest
from fastapi import HTTPException

from app.schemas.session import SessionRegister
from app.schemas.lease import LeaseAcquireRequest, LeaseHeartbeatRequest, LeaseReleaseRequest
from app.services.session_service import register_session
from app.services.lease_service import (
    acquire_lease, heartbeat_lease, release_lease,
    get_active_leases, get_resource_lease,
)


def _make_session(db, name="test"):
    return register_session(db, SessionRegister(display_name=name))


def test_acquire_empty_resource(db):
    s = _make_session(db, "acquirer")
    lease = acquire_lease(db, LeaseAcquireRequest(session_id=s.id))
    assert lease.state == "active"
    assert lease.resource_key == "shared-dev"
    assert lease.session_id == s.id


def test_acquire_while_active_fails(db):
    s1 = _make_session(db, "owner")
    s2 = _make_session(db, "contender")
    acquire_lease(db, LeaseAcquireRequest(session_id=s1.id))
    with pytest.raises(HTTPException) as exc:
        acquire_lease(db, LeaseAcquireRequest(session_id=s2.id))
    assert exc.value.status_code == 409


def test_heartbeat_extends_lease(db):
    s = _make_session(db, "hb")
    lease = acquire_lease(db, LeaseAcquireRequest(session_id=s.id, ttl_seconds=60))
    old_expires = lease.expires_at
    updated = heartbeat_lease(db, LeaseHeartbeatRequest(session_id=s.id))
    assert updated.expires_at >= old_expires


def test_release_frees_resource(db):
    s = _make_session(db, "releaser")
    acquire_lease(db, LeaseAcquireRequest(session_id=s.id))
    released = release_lease(db, LeaseReleaseRequest(session_id=s.id, release_reason="done"))
    assert released.state == "released"

    # Resource should now be available
    current = get_resource_lease(db, "shared-dev")
    assert current is None


def test_acquire_after_release(db):
    s1 = _make_session(db, "first")
    s2 = _make_session(db, "second")
    acquire_lease(db, LeaseAcquireRequest(session_id=s1.id))
    release_lease(db, LeaseReleaseRequest(session_id=s1.id))
    lease = acquire_lease(db, LeaseAcquireRequest(session_id=s2.id))
    assert lease.session_id == s2.id


def test_expire_stale_lease_then_acquire(db):
    s1 = _make_session(db, "stale")
    s2 = _make_session(db, "fresh")
    lease = acquire_lease(db, LeaseAcquireRequest(session_id=s1.id, ttl_seconds=1))
    # Force expiration by backdating
    from app.models.lease import Lease
    db_lease = db.query(Lease).filter(Lease.id == lease.id).first()
    db_lease.expires_at = datetime.now(timezone.utc) - timedelta(seconds=10)
    db.commit()

    # Should succeed because stale lease gets expired
    new_lease = acquire_lease(db, LeaseAcquireRequest(session_id=s2.id))
    assert new_lease.session_id == s2.id


def test_wrong_session_cannot_release(db):
    s1 = _make_session(db, "owner")
    s2 = _make_session(db, "intruder")
    acquire_lease(db, LeaseAcquireRequest(session_id=s1.id))
    with pytest.raises(HTTPException) as exc:
        release_lease(db, LeaseReleaseRequest(session_id=s2.id))
    assert exc.value.status_code == 404


def test_active_leases(db):
    s = _make_session(db, "active-test")
    acquire_lease(db, LeaseAcquireRequest(session_id=s.id))
    active = get_active_leases(db)
    assert len(active) >= 1
