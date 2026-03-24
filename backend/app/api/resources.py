"""Resource API endpoints."""

from __future__ import annotations

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.db.engine import get_db
from app.schemas.resource import ResourceCreate, ResourceUpdate, ResourceResponse
from app.services import resource_service

router = APIRouter(prefix="/resources", tags=["resources"])


@router.get("", response_model=list[ResourceResponse])
def list_resources(db: Session = Depends(get_db)):
    return resource_service.list_resources(db)


@router.post("", response_model=ResourceResponse)
def create_resource(data: ResourceCreate, db: Session = Depends(get_db)):
    return resource_service.create_resource(db, data)


@router.patch("/{key}", response_model=ResourceResponse)
def update_resource(key: str, data: ResourceUpdate, db: Session = Depends(get_db)):
    return resource_service.update_resource(db, key, data)
