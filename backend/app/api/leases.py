"""Lease API endpoints."""

from __future__ import annotations

from typing import Optional

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.db.engine import get_db
from app.schemas.lease import (
    LeaseAcquireRequest, LeaseHeartbeatRequest, LeaseReleaseRequest, LeaseResponse
)
from app.services import lease_service

router = APIRouter(prefix="/leases", tags=["leases"])


@router.post("/acquire", response_model=LeaseResponse)
def acquire_lease(data: LeaseAcquireRequest, db: Session = Depends(get_db)):
    return lease_service.acquire_lease(db, data)


@router.post("/heartbeat", response_model=LeaseResponse)
def heartbeat_lease(data: LeaseHeartbeatRequest, db: Session = Depends(get_db)):
    return lease_service.heartbeat_lease(db, data)


@router.post("/release", response_model=LeaseResponse)
def release_lease(data: LeaseReleaseRequest, db: Session = Depends(get_db)):
    return lease_service.release_lease(db, data)


@router.get("/active", response_model=list[LeaseResponse])
def get_active_leases(db: Session = Depends(get_db)):
    return lease_service.get_active_leases(db)


@router.get("/history", response_model=list[LeaseResponse])
def get_lease_history(resource_key: str | None = None, limit: int = 50, db: Session = Depends(get_db)):
    return lease_service.get_lease_history(db, resource_key=resource_key, limit=limit)


@router.get("/resource/{resource_key}", response_model=Optional[LeaseResponse])
def get_resource_lease(resource_key: str, db: Session = Depends(get_db)):
    lease = lease_service.get_resource_lease(db, resource_key)
    if not lease:
        return None
    return lease
