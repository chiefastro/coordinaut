"""Coordinaut CLI — main entry point."""

import json
import os
import subprocess
import sys

import typer
from rich.console import Console
from rich.table import Table

from coordinaut_cli.client import api_get, api_post, api_patch, get_api_url

app = typer.Typer(name="coordinaut", help="Local-first coordination for coding agents")
console = Console()

# --- Global options ---
json_output = False


def set_json(val: bool):
    global json_output
    json_output = val


def output(data, title: str = ""):
    if json_output:
        console.print_json(json.dumps(data, default=str))
    else:
        if isinstance(data, dict):
            for k, v in data.items():
                console.print(f"  [bold]{k}[/bold]: {v}")
        elif isinstance(data, list):
            if title:
                console.print(f"\n[bold]{title}[/bold]")
            for item in data:
                if isinstance(item, dict):
                    console.print("  ---")
                    for k, v in item.items():
                        console.print(f"    [bold]{k}[/bold]: {v}")


# ===== SESSION =====
session_app = typer.Typer(name="session", help="Manage agent sessions")
app.add_typer(session_app)


@session_app.command("register")
def session_register(
    agent_type: str = typer.Option("claude_code", help="Agent type"),
    name: str = typer.Option("", "--name", help="Display name"),
    worktree: str = typer.Option(None, help="Worktree path"),
    branch: str = typer.Option(None, help="Branch name"),
    repo: str = typer.Option(None, help="Repo path"),
    ticket: str = typer.Option(None, help="Ticket identifier"),
    pid: int = typer.Option(None, help="Process ID"),
    use_json: bool = typer.Option(False, "--json", help="JSON output"),
):
    """Register a new agent session."""
    set_json(use_json)
    # Auto-detect git info if not provided
    if not branch:
        try:
            branch = subprocess.check_output(
                ["git", "rev-parse", "--abbrev-ref", "HEAD"], stderr=subprocess.DEVNULL
            ).decode().strip()
        except Exception:
            pass
    if not worktree:
        try:
            worktree = subprocess.check_output(
                ["git", "rev-parse", "--show-toplevel"], stderr=subprocess.DEVNULL
            ).decode().strip()
        except Exception:
            pass

    data = {
        "agent_type": agent_type,
        "display_name": name,
        "worktree_path": worktree,
        "branch_name": branch,
        "repo_path": repo,
        "ticket_id": ticket,
        "pid": pid or os.getpid(),
    }
    result = api_post("/sessions/register", data)
    output(result)
    if not use_json:
        console.print(f"\n[green]Session registered: {result['id']}[/green]")


@session_app.command("heartbeat")
def session_heartbeat(
    session_id: str = typer.Argument(..., help="Session ID"),
    use_json: bool = typer.Option(False, "--json", help="JSON output"),
):
    """Heartbeat an active session."""
    set_json(use_json)
    result = api_post(f"/sessions/{session_id}/heartbeat")
    output(result)


@session_app.command("status")
def session_status(
    session_id: str = typer.Argument(..., help="Session ID"),
    status: str = typer.Argument(..., help="New status"),
    summary: str = typer.Option(None, help="Status summary"),
    use_json: bool = typer.Option(False, "--json", help="JSON output"),
):
    """Update session workflow status."""
    set_json(use_json)
    result = api_post(f"/sessions/{session_id}/status", {"status": status, "summary": summary})
    output(result)


@session_app.command("end")
def session_end(
    session_id: str = typer.Argument(..., help="Session ID"),
    use_json: bool = typer.Option(False, "--json", help="JSON output"),
):
    """End a session."""
    set_json(use_json)
    result = api_post(f"/sessions/{session_id}/end")
    output(result)


@session_app.command("list")
def session_list(
    active_only: bool = typer.Option(False, "--active", help="Active sessions only"),
    use_json: bool = typer.Option(False, "--json", help="JSON output"),
):
    """List sessions."""
    set_json(use_json)
    result = api_get("/sessions", {"active_only": active_only})
    if use_json:
        output(result)
    else:
        table = Table(title="Sessions")
        table.add_column("ID", style="dim", max_width=8)
        table.add_column("Name")
        table.add_column("Agent")
        table.add_column("Branch")
        table.add_column("Ticket")
        table.add_column("Status")
        table.add_column("Started")
        for s in result:
            table.add_row(
                s["id"][:8], s["display_name"], s["agent_type"],
                s.get("branch_name", ""), s.get("ticket_id", ""),
                s["status"], s["started_at"][:19],
            )
        console.print(table)


# ===== LEASE =====
lease_app = typer.Typer(name="lease", help="Manage resource leases")
app.add_typer(lease_app)


@lease_app.command("acquire")
def lease_acquire(
    session_id: str = typer.Argument(..., help="Session ID"),
    resource: str = typer.Option("shared-dev", help="Resource key"),
    ticket: str = typer.Option(None, help="Ticket identifier"),
    commit: str = typer.Option(None, help="Commit SHA"),
    ttl: int = typer.Option(None, help="TTL in seconds"),
    use_json: bool = typer.Option(False, "--json", help="JSON output"),
):
    """Acquire a lease on a resource."""
    set_json(use_json)
    data = {
        "resource_key": resource,
        "session_id": session_id,
        "ticket_identifier": ticket,
        "commit_sha": commit,
        "ttl_seconds": ttl,
    }
    result = api_post("/leases/acquire", data)
    output(result)
    if not use_json:
        console.print(f"\n[green]Lease acquired! Expires: {result['expires_at']}[/green]")


@lease_app.command("heartbeat")
def lease_heartbeat(
    session_id: str = typer.Argument(..., help="Session ID"),
    resource: str = typer.Option("shared-dev", help="Resource key"),
    extend: int = typer.Option(None, help="Extend by seconds"),
    use_json: bool = typer.Option(False, "--json", help="JSON output"),
):
    """Heartbeat a lease."""
    set_json(use_json)
    data = {"resource_key": resource, "session_id": session_id, "extend_seconds": extend}
    result = api_post("/leases/heartbeat", data)
    output(result)


@lease_app.command("release")
def lease_release(
    session_id: str = typer.Argument(..., help="Session ID"),
    resource: str = typer.Option("shared-dev", help="Resource key"),
    reason: str = typer.Option(None, help="Release reason"),
    use_json: bool = typer.Option(False, "--json", help="JSON output"),
):
    """Release a lease."""
    set_json(use_json)
    data = {"resource_key": resource, "session_id": session_id, "release_reason": reason}
    result = api_post("/leases/release", data)
    output(result)
    if not use_json:
        console.print("[green]Lease released.[/green]")


@lease_app.command("status")
def lease_status(
    resource: str = typer.Option("shared-dev", help="Resource key"),
    use_json: bool = typer.Option(False, "--json", help="JSON output"),
):
    """Show active lease for a resource."""
    set_json(use_json)
    result = api_get(f"/leases/resource/{resource}")
    if result:
        output(result)
    else:
        console.print(f"[dim]No active lease on {resource}[/dim]")


# ===== QUEUE =====
queue_app = typer.Typer(name="queue", help="Manage resource queue")
app.add_typer(queue_app)


@queue_app.command("enqueue")
def queue_enqueue(
    session_id: str = typer.Argument(..., help="Session ID"),
    resource: str = typer.Option("shared-dev", help="Resource key"),
    ticket: str = typer.Option(None, help="Ticket identifier"),
    priority: int = typer.Option(0, help="Priority (higher = sooner)"),
    use_json: bool = typer.Option(False, "--json", help="JSON output"),
):
    """Enqueue for a resource."""
    set_json(use_json)
    data = {
        "resource_key": resource,
        "session_id": session_id,
        "ticket_identifier": ticket,
        "priority": priority,
    }
    result = api_post("/queue/enqueue", data)
    output(result)
    if not use_json:
        console.print(f"[green]Enqueued. Entry ID: {result['id']}[/green]")


@queue_app.command("cancel")
def queue_cancel(
    entry_id: str = typer.Argument(..., help="Queue entry ID"),
    use_json: bool = typer.Option(False, "--json", help="JSON output"),
):
    """Cancel a queue entry."""
    set_json(use_json)
    result = api_post(f"/queue/{entry_id}/cancel")
    output(result)


@queue_app.command("list")
def queue_list(
    resource: str = typer.Option(None, help="Filter by resource"),
    use_json: bool = typer.Option(False, "--json", help="JSON output"),
):
    """List queue entries."""
    set_json(use_json)
    if resource:
        result = api_get(f"/queue/{resource}")
    else:
        result = api_get("/queue")
    if use_json:
        output(result)
    else:
        table = Table(title="Queue")
        table.add_column("#", style="dim")
        table.add_column("Resource")
        table.add_column("Session")
        table.add_column("Ticket")
        table.add_column("Priority")
        table.add_column("Requested")
        for i, e in enumerate(result, 1):
            table.add_row(
                str(i), e["resource_key"], e["session_id"][:8],
                e.get("ticket_identifier", ""), str(e["priority"]),
                e["requested_at"][:19],
            )
        console.print(table)


# ===== MESSAGES =====
msg_app = typer.Typer(name="msg", help="Shared context messages")
app.add_typer(msg_app)


@msg_app.command("post")
def msg_post(
    message: str = typer.Argument(..., help="Message text"),
    channel: str = typer.Option("common", help="Channel"),
    author: str = typer.Option("human", "--author", help="Author name"),
    author_type: str = typer.Option("human", "--type", help="Author type"),
    session_id: str = typer.Option(None, help="Session ID"),
    ticket: str = typer.Option(None, help="Ticket identifier"),
    use_json: bool = typer.Option(False, "--json", help="JSON output"),
):
    """Post a message."""
    set_json(use_json)
    data = {
        "channel": channel,
        "author_type": author_type,
        "author_name": author,
        "session_id": session_id,
        "ticket_identifier": ticket,
        "message": message,
    }
    result = api_post("/messages", data)
    output(result)
    if not use_json:
        console.print("[green]Message posted.[/green]")


@msg_app.command("list")
def msg_list(
    channel: str = typer.Option(None, help="Filter by channel"),
    limit: int = typer.Option(20, help="Max messages"),
    use_json: bool = typer.Option(False, "--json", help="JSON output"),
):
    """List messages."""
    set_json(use_json)
    if channel:
        result = api_get(f"/messages/channel/{channel}", {"limit": limit})
    else:
        result = api_get("/messages", {"limit": limit})
    if use_json:
        output(result)
    else:
        for m in reversed(result):
            ts = m["created_at"][:19]
            console.print(f"[dim]{ts}[/dim] [bold]#{m['channel']}[/bold] [{m['author_type']}] {m['author_name']}: {m['message']}")


# ===== TICKET =====
ticket_app = typer.Typer(name="ticket", help="Manage tickets")
app.add_typer(ticket_app)


@ticket_app.command("list")
def ticket_list(
    use_json: bool = typer.Option(False, "--json", help="JSON output"),
):
    """List tickets."""
    set_json(use_json)
    result = api_get("/tickets")
    if use_json:
        output(result)
    else:
        table = Table(title="Tickets")
        table.add_column("Identifier")
        table.add_column("Title")
        table.add_column("State")
        table.add_column("Assignee")
        table.add_column("Source")
        for t in result:
            table.add_row(
                t["identifier"], t["title"][:60], t["state"],
                t.get("assignee", ""), t["source"],
            )
        console.print(table)


@ticket_app.command("import-linear")
def ticket_import_linear(
    use_json: bool = typer.Option(False, "--json", help="JSON output"),
):
    """Import tickets from Linear."""
    set_json(use_json)
    result = api_post("/tickets/import/linear")
    if use_json:
        output(result)
    else:
        console.print(f"[green]Imported {len(result)} tickets from Linear.[/green]")


# ===== SERVE =====
@app.command("serve")
def serve(
    host: str = typer.Option("127.0.0.1", help="Host"),
    port: int = typer.Option(8787, help="Port"),
):
    """Start the Coordinaut API server."""
    import uvicorn
    console.print(f"[bold]Starting Coordinaut on {host}:{port}[/bold]")
    uvicorn.run("app.main:app", host=host, port=port, reload=False)


# ===== INIT =====
@app.command("init")
def init():
    """Initialize Coordinaut locally."""
    from pathlib import Path
    data_dir = Path.home() / ".coordinaut"
    data_dir.mkdir(parents=True, exist_ok=True)
    console.print(f"[green]Coordinaut initialized.[/green]")
    console.print(f"  Data directory: {data_dir}")
    console.print(f"  Run [bold]coordinaut serve[/bold] to start the API server.")


# ===== LAUNCH =====
launch_app = typer.Typer(name="launch", help="Launch agents")
app.add_typer(launch_app)


@launch_app.command("agent")
def launch_agent(
    ticket: str = typer.Option(..., "--ticket", help="Ticket identifier"),
    template: str = typer.Option("default", help="Template name"),
    use_json: bool = typer.Option(False, "--json", help="JSON output"),
):
    """Launch an agent for a ticket."""
    set_json(use_json)
    data = {"ticket_identifier": ticket, "template_name": template}
    result = api_post("/launch/agent", data)
    output(result)


if __name__ == "__main__":
    app()
