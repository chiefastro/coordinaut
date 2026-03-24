# Implementation Decisions

## Python tooling
- **Package manager**: hatchling (modern, PEP 621 compliant)
- **ORM**: SQLAlchemy 2.0 with mapped_column declarative style
- **Migration strategy**: Schema created at startup via `Base.metadata.create_all()`. Alembic available as dependency for future use.
- **Python 3.9 compatibility**: Using `from __future__ import annotations` + `eval_type_backport` for Pydantic, and `Optional[]` for SQLAlchemy `Mapped[]` types.

## Lease constraint implementation
- At-most-one-active-lease enforced at application level: `acquire_lease` checks for existing active lease in a transaction before creating a new one.
- Stale leases are expired (checked on acquire and on reads) rather than requiring a background task.
- SQLite WAL mode enabled for better concurrent read performance.

## Queue policy
- FIFO with optional static priority (higher priority value = earlier in queue).
- Queue is advisory: it shows waiting order but `acquire` is the authoritative operation.
- Duplicate enqueue for same session+resource is rejected.

## UI polling interval
- Dashboard/leases: 3-5 second polling
- Events/messages: 5 second polling
- Tickets: 10 second polling
- No websockets/SSE for MVP — polling is sufficient for single-user local use.

## Launcher implementation
- Shell-based: templates define a command string with `{ticket_identifier}`, `{ticket_title}` substitution variables.
- Templates loaded from a JSON config file or fall back to a default Claude Code template.
- `subprocess.Popen` with `start_new_session=True` for process independence.

## Linear integration
- GraphQL API with `httpx` for HTTP calls.
- Upsert strategy: existing tickets matched by `identifier` are updated on reimport.
- Graceful degradation: if Linear credentials are missing, the endpoint returns a 400 with instructions rather than crashing.

## CLI packaging
- CLI and backend share one Python package installed via `pip install -e .`
- CLI uses `httpx` to call the local API (same as any external client would).
- Auto-detects git branch and worktree path during `session register`.
