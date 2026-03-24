"""Queue API endpoints."""

from __future__ import annotations

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.db.engine import get_db
from app.schemas.queue import QueueEnqueueRequest, QueueEntryResponse
from app.services import queue_service

router = APIRouter(prefix="/queue", tags=["queue"])


@router.post("/enqueue", response_model=QueueEntryResponse)
def enqueue(data: QueueEnqueueRequest, db: Session = Depends(get_db)):
    return queue_service.enqueue(db, data)


@router.post("/{entry_id}/cancel", response_model=QueueEntryResponse)
def cancel_entry(entry_id: str, db: Session = Depends(get_db)):
    return queue_service.cancel_entry(db, entry_id)


@router.get("", response_model=list[QueueEntryResponse])
def list_all_queue(db: Session = Depends(get_db)):
    return queue_service.list_queue_all(db)


@router.get("/{resource_key}", response_model=list[QueueEntryResponse])
def list_resource_queue(resource_key: str, db: Session = Depends(get_db)):
    return queue_service.list_queue(db, resource_key=resource_key)
