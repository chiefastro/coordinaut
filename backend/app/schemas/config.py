"""Config schemas."""

from __future__ import annotations

from pydantic import BaseModel


class ConfigUpdate(BaseModel):
    values: dict[str, str]


class ConfigResponse(BaseModel):
    config: dict[str, str]
