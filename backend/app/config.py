"""Application configuration."""

from __future__ import annotations

import os
from pathlib import Path

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Coordinaut configuration loaded from environment variables."""

    # Database
    database_url: str = ""
    db_path: str = ""

    # API
    api_host: str = "127.0.0.1"
    api_port: int = 8787
    cors_origins: list[str] = ["http://localhost:5173", "http://127.0.0.1:5173"]

    # Lease defaults
    default_lease_ttl_seconds: int = 600  # 10 minutes

    # Linear integration
    linear_api_key: str = ""
    linear_team_id: str = ""

    # Launcher
    launcher_config_path: str = ""

    # Target repos (comma-separated paths)
    target_repos: str = ""

    # Data directory
    data_dir: str = ""

    model_config = {
        "env_prefix": "COORDINAUT_",
        "env_file": [".env", "../.env"],
    }

    def get_data_dir(self) -> Path:
        if self.data_dir:
            p = Path(self.data_dir)
        else:
            p = Path.home() / ".coordinaut"
        p.mkdir(parents=True, exist_ok=True)
        return p

    def get_db_url(self) -> str:
        if self.database_url:
            return self.database_url
        db_path = self.db_path or str(self.get_data_dir() / "coordinaut.db")
        return f"sqlite:///{db_path}"


settings = Settings()
