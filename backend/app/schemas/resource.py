"""Resource schemas."""

from __future__ import annotations

from pydantic import BaseModel


class ResourceCreate(BaseModel):
    key: str
    name: str
    description: str = ""
    lease_ttl_seconds: int = 600
    is_enabled: bool = True
    metadata_json: str | None = None


class ResourceUpdate(BaseModel):
    name: str | None = None
    description: str | None = None
    lease_ttl_seconds: int | None = None
    is_enabled: bool | None = None
    metadata_json: str | None = None


class ResourceResponse(BaseModel):
    id: str
    key: str
    name: str
    description: str
    lease_ttl_seconds: int
    is_enabled: bool
    metadata_json: str | None

    model_config = {"from_attributes": True}
