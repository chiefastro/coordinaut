# Coordinaut

Local-first coordination layer for autonomous coding workflows. Coordinates multiple coding agents working against a shared development environment.

## What it does

- **Lease-based coordination**: Only one agent can hold the shared-dev environment at a time
- **Queue management**: Agents wait in line with FIFO + priority ordering
- **Session tracking**: See all active coding agents, their branches, tickets, and workflow status
- **Shared messaging**: Agents and humans post context, notes, and handoff info
- **Ticket integration**: Import from Linear, launch agents from tickets
- **Localhost UI**: Dashboard showing active sessions, lease owner, queue, events, and messages

## Quick Start

### 1. Install

```bash
cd backend
python3 -m venv .venv
source .venv/bin/activate
pip install -e ".[dev]"
```

### 2. Initialize and run

```bash
# From backend/
coordinaut init
coordinaut serve
```

API runs on `http://127.0.0.1:8787`.

### 3. Run the UI

```bash
cd frontend
npm install
npm run dev
```

UI runs on `http://localhost:5173`.

### 4. Use the CLI

```bash
# Register a session
coordinaut session register --name "my-agent" --ticket ABC-123

# Acquire shared-dev lease
coordinaut lease acquire <session-id>

# Heartbeat the lease
coordinaut lease heartbeat <session-id>

# Release when done
coordinaut lease release <session-id>

# Post a message
coordinaut msg post "Deploy succeeded, tests passing"

# List sessions
coordinaut session list

# Check lease status
coordinaut lease status
```

## Architecture

```
SQLite ← FastAPI API → CLI (Typer + httpx)
                    → Web UI (React + Vite)
                    → Linear integration
                    → Agent launcher
```

## Configuration

Environment variables (prefix `COORDINAUT_`):

| Variable | Default | Description |
|---|---|---|
| `COORDINAUT_API_HOST` | `127.0.0.1` | API bind host |
| `COORDINAUT_API_PORT` | `8787` | API bind port |
| `COORDINAUT_DB_PATH` | `~/.coordinaut/coordinaut.db` | SQLite database path |
| `COORDINAUT_DEFAULT_LEASE_TTL_SECONDS` | `600` | Default lease TTL (10 min) |
| `COORDINAUT_LINEAR_API_KEY` | | Linear API key for ticket import |
| `COORDINAUT_LINEAR_TEAM_ID` | | Linear team ID |
| `COORDINAUT_LAUNCHER_CONFIG_PATH` | | Path to launcher templates JSON |

## Testing

```bash
cd backend
source .venv/bin/activate
PYTHONPATH=. python -m pytest ../tests/ -v
```

## Project Structure

```
backend/
  app/
    api/          # FastAPI route handlers
    models/       # SQLAlchemy models
    services/     # Business logic
    schemas/      # Pydantic request/response models
    integrations/ # Linear sync
    launcher/     # Agent launch service
    db/           # Database engine + session
    config.py     # Settings
    main.py       # FastAPI app
cli/
  coordinaut_cli/ # Typer CLI
frontend/
  src/
    components/   # React page components
    api.ts        # API client
    types.ts      # TypeScript types
tests/            # pytest tests
docs/             # Design decisions
```

## Status

MVP — functional for local single-user coordination of multiple coding agents.
