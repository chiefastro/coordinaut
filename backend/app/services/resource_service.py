"""Resource service."""

from __future__ import annotations

from fastapi import HTTPException
from sqlalchemy.orm import Session

from app.models.resource import Resource
from app.schemas.resource import ResourceCreate, ResourceUpdate


def create_resource(db: Session, data: ResourceCreate) -> Resource:
    existing = db.query(Resource).filter(Resource.key == data.key).first()
    if existing:
        raise HTTPException(status_code=409, detail=f"Resource '{data.key}' already exists")
    resource = Resource(
        key=data.key,
        name=data.name,
        description=data.description,
        lease_ttl_seconds=data.lease_ttl_seconds,
        is_enabled=data.is_enabled,
        metadata_json=data.metadata_json,
    )
    db.add(resource)
    db.commit()
    db.refresh(resource)
    return resource


def update_resource(db: Session, key: str, data: ResourceUpdate) -> Resource:
    resource = db.query(Resource).filter(Resource.key == key).first()
    if not resource:
        raise HTTPException(status_code=404, detail=f"Resource '{key}' not found")
    for field, val in data.model_dump(exclude_unset=True).items():
        setattr(resource, field, val)
    db.commit()
    db.refresh(resource)
    return resource


def list_resources(db: Session) -> list[Resource]:
    return db.query(Resource).all()


def seed_default_resource(db: Session) -> None:
    """Ensure shared-dev resource exists."""
    existing = db.query(Resource).filter(Resource.key == "shared-dev").first()
    if not existing:
        resource = Resource(
            key="shared-dev",
            name="Shared Dev Environment",
            description="The shared mutable development environment",
            lease_ttl_seconds=600,
            is_enabled=True,
        )
        db.add(resource)
        db.commit()
