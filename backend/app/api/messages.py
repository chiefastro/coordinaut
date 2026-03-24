"""Message API endpoints."""

from __future__ import annotations

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.db.engine import get_db
from app.schemas.message import MessageCreate, MessageResponse
from app.services import message_service

router = APIRouter(prefix="/messages", tags=["messages"])


@router.post("", response_model=MessageResponse)
def post_message(data: MessageCreate, db: Session = Depends(get_db)):
    return message_service.post_message(db, data)


@router.get("", response_model=list[MessageResponse])
def list_messages(limit: int = 100, db: Session = Depends(get_db)):
    return message_service.list_messages(db, limit=limit)


@router.get("/channel/{channel:path}", response_model=list[MessageResponse])
def list_channel_messages(channel: str, limit: int = 100, db: Session = Depends(get_db)):
    return message_service.list_messages(db, limit=limit, channel=channel)
