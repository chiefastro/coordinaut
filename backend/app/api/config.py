"""Config API endpoints."""

import json
from datetime import datetime, timezone

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.db.engine import get_db
from app.models.app_config import AppConfig
from app.schemas.config import ConfigUpdate, ConfigResponse

router = APIRouter(prefix="/config", tags=["config"])


@router.get("", response_model=ConfigResponse)
def get_config(db: Session = Depends(get_db)):
    rows = db.query(AppConfig).all()
    config = {}
    for row in rows:
        try:
            config[row.key] = json.loads(row.value_json)
        except (json.JSONDecodeError, TypeError):
            config[row.key] = row.value_json
    return ConfigResponse(config=config)


@router.patch("", response_model=ConfigResponse)
def update_config(data: ConfigUpdate, db: Session = Depends(get_db)):
    now = datetime.now(timezone.utc)
    for key, value in data.values.items():
        existing = db.query(AppConfig).filter(AppConfig.key == key).first()
        val_json = json.dumps(value) if not isinstance(value, str) else value
        if existing:
            existing.value_json = val_json
            existing.updated_at = now
        else:
            db.add(AppConfig(key=key, value_json=val_json, updated_at=now))
    db.commit()
    return get_config(db=db)
