"""Launcher API endpoints."""

from __future__ import annotations

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.db.engine import get_db
from app.schemas.launcher import LaunchRequest, LaunchResponse, LaunchTemplate
from app.launcher.service import launch_agent, get_templates

router = APIRouter(prefix="/launch", tags=["launcher"])


@router.post("/agent", response_model=LaunchResponse)
def launch(data: LaunchRequest, db: Session = Depends(get_db)):
    return launch_agent(db, data)


@router.get("/templates", response_model=dict[str, LaunchTemplate])
def list_templates():
    return get_templates()
