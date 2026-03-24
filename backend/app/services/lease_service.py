"""Lease management service — the core coordination primitive."""

from __future__ import annotations

from datetime import datetime, timezone, timedelta

from fastapi import HTTPException
from sqlalchemy.orm import Session

from app.models.lease import Lease
from app.models.resource import Resource
from app.schemas.lease import LeaseAcquireRequest, LeaseHeartbeatRequest, LeaseReleaseRequest
from app.services.event_service import log_event


def _expire_stale_leases(db: Session, resource_key: str) -> None:
    """Mark expired leases before checking availability."""
    now = datetime.now(timezone.utc)
    stale = (
        db.query(Lease)
        .filter(Lease.resource_key == resource_key, Lease.state == "active", Lease.expires_at < now)
        .all()
    )
    for lease in stale:
        lease.state = "expired"
        lease.released_at = now
        lease.release_reason = "TTL expired"
        log_event(db, "lease_expired", f"Lease expired for {resource_key}",
                  session_id=lease.session_id, resource_key=resource_key)
    if stale:
        db.flush()


def acquire_lease(db: Session, data: LeaseAcquireRequest) -> Lease:
    resource = db.query(Resource).filter(Resource.key == data.resource_key).first()
    if not resource:
        raise HTTPException(status_code=404, detail=f"Resource '{data.resource_key}' not found")
    if not resource.is_enabled:
        raise HTTPException(status_code=400, detail=f"Resource '{data.resource_key}' is disabled")

    _expire_stale_leases(db, data.resource_key)

    active = (
        db.query(Lease)
        .filter(Lease.resource_key == data.resource_key, Lease.state == "active")
        .first()
    )
    if active:
        raise HTTPException(
            status_code=409,
            detail=f"Resource '{data.resource_key}' is currently leased by session {active.session_id}",
        )

    ttl = data.ttl_seconds or resource.lease_ttl_seconds
    now = datetime.now(timezone.utc)
    lease = Lease(
        resource_key=data.resource_key,
        session_id=data.session_id,
        ticket_identifier=data.ticket_identifier,
        commit_sha=data.commit_sha,
        state="active",
        acquired_at=now,
        expires_at=now + timedelta(seconds=ttl),
        heartbeat_at=now,
        metadata_json=data.metadata_json,
    )
    db.add(lease)
    log_event(db, "lease_acquired", f"Lease acquired for {data.resource_key}",
              session_id=data.session_id, resource_key=data.resource_key,
              ticket_identifier=data.ticket_identifier)
    db.commit()
    db.refresh(lease)
    return lease


def heartbeat_lease(db: Session, data: LeaseHeartbeatRequest) -> Lease:
    _expire_stale_leases(db, data.resource_key)

    lease = (
        db.query(Lease)
        .filter(
            Lease.resource_key == data.resource_key,
            Lease.session_id == data.session_id,
            Lease.state == "active",
        )
        .first()
    )
    if not lease:
        raise HTTPException(status_code=404, detail="No active lease found for this session/resource")

    now = datetime.now(timezone.utc)
    extend = data.extend_seconds or 0
    if extend > 0:
        lease.expires_at = lease.expires_at + timedelta(seconds=extend)
    else:
        resource = db.query(Resource).filter(Resource.key == data.resource_key).first()
        lease.expires_at = now + timedelta(seconds=resource.lease_ttl_seconds)

    lease.heartbeat_at = now
    log_event(db, "lease_heartbeat", f"Lease heartbeat for {data.resource_key}",
              session_id=data.session_id, resource_key=data.resource_key)
    db.commit()
    db.refresh(lease)
    return lease


def release_lease(db: Session, data: LeaseReleaseRequest) -> Lease:
    lease = (
        db.query(Lease)
        .filter(
            Lease.resource_key == data.resource_key,
            Lease.session_id == data.session_id,
            Lease.state == "active",
        )
        .first()
    )
    if not lease:
        raise HTTPException(status_code=404, detail="No active lease found for this session/resource")

    now = datetime.now(timezone.utc)
    lease.state = "released"
    lease.released_at = now
    lease.release_reason = data.release_reason or "voluntary release"
    log_event(db, "lease_released", f"Lease released for {data.resource_key}",
              session_id=data.session_id, resource_key=data.resource_key)
    db.commit()
    db.refresh(lease)
    return lease


def get_active_leases(db: Session) -> list[Lease]:
    _expire_stale_leases_all(db)
    return db.query(Lease).filter(Lease.state == "active").all()


def get_lease_history(db: Session, resource_key: str | None = None, limit: int = 50) -> list[Lease]:
    q = db.query(Lease)
    if resource_key:
        q = q.filter(Lease.resource_key == resource_key)
    return q.order_by(Lease.acquired_at.desc()).limit(limit).all()


def get_resource_lease(db: Session, resource_key: str) -> Lease | None:
    _expire_stale_leases(db, resource_key)
    return (
        db.query(Lease)
        .filter(Lease.resource_key == resource_key, Lease.state == "active")
        .first()
    )


def _expire_stale_leases_all(db: Session) -> None:
    now = datetime.now(timezone.utc)
    stale = db.query(Lease).filter(Lease.state == "active", Lease.expires_at < now).all()
    for lease in stale:
        lease.state = "expired"
        lease.released_at = now
        lease.release_reason = "TTL expired"
    if stale:
        db.commit()
