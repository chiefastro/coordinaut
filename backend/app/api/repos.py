"""Repository info API endpoints."""

from __future__ import annotations

from fastapi import APIRouter

from app.services.repo_service import get_all_repos_info, get_repo_info, discover_claude_sessions

router = APIRouter(prefix="/repos", tags=["repos"])


@router.get("")
def list_repos():
    """Get git info for all target repos."""
    return get_all_repos_info()


@router.get("/sessions")
def discover_sessions():
    """Discover running Claude Code processes."""
    return discover_claude_sessions()
