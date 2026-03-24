"""Repository inspection service — discovers git info for target repos."""

from __future__ import annotations

import subprocess
from pathlib import Path

from app.config import settings


def get_target_repos() -> list[str]:
    """Return list of configured target repo paths."""
    if not settings.target_repos:
        return []
    return [p.strip() for p in settings.target_repos.split(",") if p.strip()]


def _git(repo_path: str, *args: str) -> str:
    """Run a git command in a repo and return stdout."""
    try:
        result = subprocess.run(
            ["git", *args],
            cwd=repo_path,
            capture_output=True,
            text=True,
            timeout=10,
        )
        return result.stdout.strip()
    except Exception:
        return ""


def get_repo_info(repo_path: str) -> dict:
    """Get git info for a repository."""
    p = Path(repo_path)
    if not p.exists():
        return {"path": repo_path, "error": "Path does not exist"}

    name = p.name
    current_branch = _git(repo_path, "rev-parse", "--abbrev-ref", "HEAD")
    remote_url = _git(repo_path, "remote", "get-url", "origin")

    # Recent commits (last 10)
    log_output = _git(repo_path, "log", "--oneline", "-10", "--format=%H|%s|%an|%ar")
    commits = []
    for line in log_output.splitlines():
        if "|" in line:
            parts = line.split("|", 3)
            if len(parts) == 4:
                commits.append({
                    "sha": parts[0][:8],
                    "message": parts[1],
                    "author": parts[2],
                    "when": parts[3],
                })

    # Branches
    branches_output = _git(repo_path, "branch", "--format=%(refname:short)|%(upstream:short)|%(HEAD)")
    branches = []
    for line in branches_output.splitlines():
        parts = line.split("|")
        if len(parts) >= 3:
            branches.append({
                "name": parts[0],
                "upstream": parts[1] or None,
                "current": parts[2].strip() == "*",
            })

    # Worktrees
    worktrees_output = _git(repo_path, "worktree", "list", "--porcelain")
    worktrees = []
    current_wt: dict = {}
    for line in worktrees_output.splitlines():
        if line.startswith("worktree "):
            if current_wt:
                worktrees.append(current_wt)
            current_wt = {"path": line[9:]}
        elif line.startswith("HEAD "):
            current_wt["head"] = line[5:][:8]
        elif line.startswith("branch "):
            current_wt["branch"] = line[7:].replace("refs/heads/", "")
        elif line == "bare":
            current_wt["bare"] = True
    if current_wt:
        worktrees.append(current_wt)

    # Status summary
    status_output = _git(repo_path, "status", "--porcelain")
    changed_files = len([l for l in status_output.splitlines() if l.strip()])

    return {
        "path": repo_path,
        "name": name,
        "current_branch": current_branch,
        "remote_url": remote_url,
        "branches": branches,
        "worktrees": worktrees,
        "recent_commits": commits,
        "changed_files": changed_files,
    }


def discover_claude_sessions() -> list[dict]:
    """Discover running Claude Code processes with their working directories."""
    try:
        result = subprocess.run(
            ["ps", "aux"],
            capture_output=True,
            text=True,
            timeout=5,
        )
        sessions = []
        seen_pids = set()
        for line in result.stdout.splitlines():
            # Match Claude Code binary processes (not helper/spawn processes)
            if "/claude" not in line:
                continue
            if "--output-format" not in line:
                continue
            parts = line.split()
            if len(parts) < 2:
                continue
            pid = parts[1]
            if pid in seen_pids:
                continue
            seen_pids.add(pid)

            # Try to get working directory via lsof
            cwd = _get_process_cwd(pid)

            # Extract resume session ID if present
            cmd = " ".join(parts[10:]) if len(parts) > 10 else ""
            resume_id = None
            if "--resume" in cmd:
                try:
                    idx = cmd.index("--resume") + len("--resume ")
                    resume_id = cmd[idx:].split()[0]
                except (ValueError, IndexError):
                    pass

            sessions.append({
                "pid": pid,
                "cwd": cwd,
                "resume_id": resume_id,
                "agent_type": "claude_code",
            })
        return sessions
    except Exception:
        return []


def _get_process_cwd(pid: str) -> str | None:
    """Get the current working directory of a process on macOS."""
    try:
        result = subprocess.run(
            ["lsof", "-p", pid, "-Fn"],
            capture_output=True,
            text=True,
            timeout=5,
        )
        # lsof output: lines starting with 'n' after 'fcwd' are the cwd
        lines = result.stdout.splitlines()
        for i, line in enumerate(lines):
            if line == "fcwd" and i + 1 < len(lines):
                return lines[i + 1][1:]  # strip leading 'n'
        return None
    except Exception:
        return None


def get_all_repos_info() -> list[dict]:
    """Get info for all target repos."""
    repos = get_target_repos()
    return [get_repo_info(r) for r in repos]
