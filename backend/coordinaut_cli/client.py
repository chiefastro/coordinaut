"""HTTP client for Coordinaut API."""

from __future__ import annotations

import json
import os

import httpx


def get_api_url() -> str:
    return os.environ.get("COORDINAUT_API_URL", "http://127.0.0.1:8787")


def api_get(path: str, params: dict | None = None) -> dict | list:
    url = f"{get_api_url()}{path}"
    resp = httpx.get(url, params=params, timeout=10)
    resp.raise_for_status()
    return resp.json()


def api_post(path: str, data: dict | None = None) -> dict:
    url = f"{get_api_url()}{path}"
    resp = httpx.post(url, json=data or {}, timeout=10)
    resp.raise_for_status()
    return resp.json()


def api_patch(path: str, data: dict | None = None) -> dict:
    url = f"{get_api_url()}{path}"
    resp = httpx.patch(url, json=data or {}, timeout=10)
    resp.raise_for_status()
    return resp.json()
