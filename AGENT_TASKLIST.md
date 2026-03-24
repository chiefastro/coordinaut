# Coordinaut Agent Task List
Status: Execution Plan
Companion doc: `SPEC.md`

This file turns the MVP spec into an implementation checklist for a coding agent.
The goal is to build a usable local-first OSS version of Coordinaut quickly, with working software prioritized over abstraction.

---

## 0. Working Rules

### Primary objective
Build a practical local-first MVP that I can use as the first customer.

### Implementation priorities
1. Working end-to-end flow
2. Local reliability
3. Inspectable state
4. Good CLI ergonomics
5. Useful localhost UI
6. Clean enough architecture to evolve later

### Avoid
- overengineering
- premature cloud abstractions
- deep plugin systems
- elaborate auth
- complex message buses
- premature multi-machine support

### Make reasonable choices
If something in the spec is ambiguous, choose the simplest practical implementation and document the decision in:
- code comments where needed
- `docs/decisions.md`

---

## 1. MVP Success Criteria

The MVP is successful when all of the following are true:

- I can run Coordinaut locally
- State persists across restarts
- I can register multiple agent sessions
- Each session can be associated with a worktree, branch, and ticket
- One session can hold the `shared-dev` lease at a time
- Other sessions can queue for `shared-dev`
- Lease TTL and heartbeat work
- I can view active sessions, queue, lease owner, and recent events in a local web UI
- I can post/read shared messages
- I can import or display Linear tickets
- I can click a ticket in the UI and launch a new agent through a configurable command template

---

## 2. Suggested Implementation Order

Build in this order unless a better sequence becomes obvious during implementation:

1. repo/project skeleton
2. backend app + config
3. SQLite schema + persistence layer
4. session APIs
5. lease APIs
6. queue APIs
7. message APIs
8. event logging
9. CLI
10. basic frontend dashboard
11. tickets + Linear integration
12. launcher
13. polish, packaging, docs, tests

---

## 3. Deliverable Breakdown

---

# Phase 1 — Project Skeleton

## Task 1.1: Create repo structure
Create a practical monorepo or near-monorepo layout.

Suggested structure:

- `/backend`
- `/backend/app`
- `/backend/app/api`
- `/backend/app/models`
- `/backend/app/services`
- `/backend/app/db`
- `/backend/app/schemas`
- `/backend/app/integrations`
- `/backend/app/launcher`
- `/frontend`
- `/frontend/src`
- `/cli`
- `/cli/coordinaut_cli`
- `/docs`
- `/tests`

### Done when
- project layout exists
- dependencies can be installed
- basic app entrypoints are stubbed

---

## Task 1.2: Choose tooling and dependency files
Set up:
- Python package management
- frontend package management
- lint/format defaults
- test framework

Recommended:
- Python: FastAPI + SQLAlchemy/SQLModel + Typer + pytest
- Frontend: React + TypeScript + Vite
- Formatting: Ruff/Black or Ruff-only if preferred

### Done when
- backend can start a hello-world API
- frontend can render a hello-world page
- CLI can print hello-world

---

## Task 1.3: Add initial docs
Create:
- `README.md`
- `docs/decisions.md`

README should include:
- what Coordinaut is
- how to run locally
- current MVP status

`docs/decisions.md` should capture key implementation decisions as they happen.

### Done when
- someone new can understand how to boot the project

---

# Phase 2 — Backend Foundation

## Task 2.1: App config system
Implement a lightweight config layer.

Support:
- database path
- API host/port
- frontend origin if needed
- Linear API token/base config
- launcher template config path
- default lease TTL

Use env vars plus optional local config file.

### Done when
- config values are centrally loaded
- app can run without fragile hardcoding

---

## Task 2.2: SQLite database setup
Implement SQLite initialization.

Requirements:
- persistent DB file
- startup initialization
- migrations or schema creation strategy
- WAL mode if useful
- practical connection/session management

### Done when
- DB file is created locally
- app can read/write test records

---

## Task 2.3: Core database schema
Create schema for:

- sessions
- tickets
- resources
- leases
- queue_entries
- workflow_events
- messages
- status_updates
- app_config

Include useful indexes.

### Important constraints
- resource keys should be unique
- at most one active lease per resource
- queue entries should be queryable by resource and requested time
- sessions should be queryable by current state and last_seen_at

### Done when
- schema exists
- DB can be initialized from scratch successfully

---

## Task 2.4: Seed default resource
On startup or init, create a default resource:
- `shared-dev`

Include:
- sensible default TTL
- name/description

### Done when
- a fresh install has a usable default resource without manual setup

---

# Phase 3 — Session Tracking

## Task 3.1: Session model and service
Implement session creation and updates.

A session should capture:
- agent type
- display name
- pid if known
- host
- worktree path
- branch name
- repo path
- ticket association
- current status
- timestamps

### Done when
- backend service can create, update, retrieve, and end sessions

---

## Task 3.2: Session API endpoints
Implement:
- register session
- heartbeat session
- update session status
- end session
- list sessions
- get session details

### Done when
- endpoints work via curl or test client

---

## Task 3.3: Session event logging
Whenever a session:
- starts
- heartbeats
- changes status
- ends

append useful event records.

### Done when
- recent events reflect session lifecycle

---

# Phase 4 — Lease System

## Task 4.1: Lease acquisition logic
Implement the core lease service.

Requirements:
- atomic lease acquisition
- check for existing active unexpired lease
- expire stale lease when appropriate
- fail cleanly if resource is owned
- support metadata like ticket and commit SHA

### Important
This is the single most important concurrency primitive in the app.

### Done when
- one session can acquire `shared-dev`
- a second session cannot acquire while lease is active

---

## Task 4.2: Lease heartbeat logic
Implement lease heartbeat.

Requirements:
- only current owner can heartbeat
- heartbeat extends expiration
- heartbeat updates timestamps
- meaningful error on invalid or expired lease

### Done when
- lease expiration can be extended repeatedly

---

## Task 4.3: Lease release logic
Implement release.

Requirements:
- only current owner can release
- release records outcome/reason
- lease state becomes historical
- resource becomes available for next queue candidate

### Done when
- lease can be released and new acquisition becomes possible

---

## Task 4.4: Lease expiry handling
Implement stale lease behavior.

Minimum acceptable approach:
- expiration checked during acquire
- expiration checked during relevant reads
- explicit cleanup function available

Optional:
- background cleanup task

### Done when
- stale lease does not permanently block the resource

---

## Task 4.5: Lease API endpoints
Implement:
- acquire
- heartbeat
- release
- active lease list
- lease history
- resource lease status

### Done when
- all lease operations are accessible over API

---

## Task 4.6: Lease tests
Write tests for:
- acquire empty resource
- acquire with active owner
- expire stale lease then acquire
- heartbeat extends lease
- release frees resource
- invalid session cannot release other session's lease

### Done when
- lease tests pass reliably

---

# Phase 5 — Queue System

## Task 5.1: Queue data/service layer
Implement queue service.

Requirements:
- enqueue session for a resource
- cancel queue entry
- list queue by resource
- FIFO ordering
- optional static priority support if easy

### MVP simplification
Do not overbuild scheduling rules.

### Done when
- multiple sessions can wait for `shared-dev` and ordering is visible

---

## Task 5.2: Queue grant behavior
Decide and implement one of:
- explicit acquire only, with queue as advisory
- or helper flow that can grant next candidate when lease is released

For MVP, either is acceptable as long as behavior is clear and documented.

Recommended:
- queue remains advisory but visible
- lease acquisition remains authoritative

### Done when
- queue reflects waiting sessions accurately

---

## Task 5.3: Queue API endpoints
Implement:
- enqueue
- cancel
- list all
- list by resource

### Done when
- queue usable from API and tests

---

## Task 5.4: Queue tests
Test:
- enqueue order
- cancellation
- visibility by resource
- interaction with lease release if any helper logic exists

### Done when
- queue behavior is predictable

---

# Phase 6 — Messages and Shared Context

## Task 6.1: Shared message model/service
Implement common-area messaging.

Support:
- channels
- author type
- author name
- optional session link
- optional ticket link
- timestamp

### Suggested default channels
- `common`
- `ticket/<identifier>`
- `resource/shared-dev`

### Done when
- messages can be posted and queried cleanly

---

## Task 6.2: Message API endpoints
Implement:
- post message
- list messages
- list by channel

### Done when
- agents and humans can use API for shared context

---

## Task 6.3: Message CLI commands
Implement:
- post message
- list messages
- list channel messages

### Done when
- shared context is usable from terminal

---

# Phase 7 — Workflow Status and Events

## Task 7.1: Canonical status enum
Implement normalized statuses:

- `idle`
- `starting`
- `local_dev`
- `blocked`
- `shared_env_enqueued`
- `shared_env_lease_acquired`
- `shared_env_deploy_running`
- `shared_env_deploy_complete`
- `shared_env_verification`
- `shared_env_released`
- `completed`
- `failed`
- `cancelled`

### Done when
- status updates are validated consistently

---

## Task 7.2: Status history
Store status update history separately from current session state.

### Done when
- UI can show both current state and recent transitions

---

## Task 7.3: Event log service
Implement append-only workflow events.

Important event types:
- session registered
- session heartbeated
- status changed
- lease acquired
- lease heartbeated
- lease released
- queue enqueued
- queue cancelled
- message posted
- launcher started
- Linear sync run

### Done when
- recent event feed can power the dashboard

---

# Phase 8 — CLI

## Task 8.1: CLI foundation
Create `coordinaut` CLI package.

Support global config:
- API URL
- session id
- JSON output
- quiet mode

### Done when
- CLI can talk to local API

---

## Task 8.2: Session CLI commands
Implement:
- `coordinaut session register`
- `coordinaut session heartbeat`
- `coordinaut session status`
- `coordinaut session end`
- `coordinaut session list`

### Done when
- agent session lifecycle can be managed entirely via CLI

---

## Task 8.3: Lease CLI commands
Implement:
- `coordinaut lease acquire`
- `coordinaut lease heartbeat`
- `coordinaut lease release`
- `coordinaut lease status`

### Done when
- shared-dev coordination is scriptable from CLI

---

## Task 8.4: Queue CLI commands
Implement:
- `coordinaut queue enqueue`
- `coordinaut queue cancel`
- `coordinaut queue list`

### Done when
- queue flow is scriptable

---

## Task 8.5: Message CLI commands
Implement:
- `coordinaut msg post`
- `coordinaut msg list`

### Done when
- agents can post shared context from shell commands

---

## Task 8.6: Init and serve commands
Implement:
- `coordinaut init`
- `coordinaut serve`

Recommended:
- `init` creates local config and DB if needed
- `serve` starts backend
- optional convenience to open UI

### Done when
- fresh local setup is smooth

---

# Phase 9 — Frontend UI

## Task 9.1: Frontend shell
Create basic React app with:
- layout
- nav
- API client
- polling-based data refresh

### Done when
- frontend can fetch and display backend health

---

## Task 9.2: Main dashboard
Display:
- active sessions count
- active lease owner
- queue length
- recent events
- expired/stale warnings if any

### Done when
- dashboard provides immediate situational awareness

---

## Task 9.3: Sessions view
Show a sessions table with:
- session name/id
- agent type
- worktree path
- branch
- ticket
- current status
- started at
- last seen
- actions if useful

### Done when
- user can inspect all active sessions clearly

---

## Task 9.4: Lease view
Show:
- current owner of `shared-dev`
- expiration countdown
- ticket
- commit SHA if known
- recent lease history

### Done when
- shared-dev ownership is obvious

---

## Task 9.5: Queue view
Show:
- resource
- position
- session
- ticket
- requested time
- priority
- state

### Done when
- waiting order is visible

---

## Task 9.6: Messages view
Show:
- common-area feed
- selectable channels
- post form
- timestamps and authors

### Done when
- humans can use the shared context feature from UI

---

## Task 9.7: Events view
Show:
- recent event stream
- filtering by session/ticket/resource if easy

### Done when
- debugging activity is easier than reading raw logs

---

# Phase 10 — Tickets and Linear Integration

## Task 10.1: Ticket model and API
Implement local ticket records and API endpoints.

Support:
- list tickets
- create manual tickets if needed
- get ticket details

### Done when
- UI has a stable ticket abstraction independent of Linear

---

## Task 10.2: Linear integration service
Implement minimal Linear fetch/import.

Requirements:
- read issues from Linear
- map to local ticket model
- store essential metadata
- safe behavior when token/config missing

### Important
Do not let Linear integration block local operation.

### Done when
- user can import tickets from Linear into local DB

---

## Task 10.3: Tickets UI
Show:
- identifier
- title
- state
- assignee
- labels
- action button to launch agent

### Done when
- user can browse tickets and act on them

---

# Phase 11 — Agent Launcher

## Task 11.1: Launcher config model
Implement configurable launch templates.

A template should support:
- name
- agent type
- base command
- working directory rules
- environment variables
- optional prompt/skill path
- optional worktree strategy

### Done when
- launch templates can be read from config

---

## Task 11.2: Basic launcher service
Implement a shell-based local launcher.

MVP requirements:
- launch a configured command for a chosen ticket
- pass useful context (ticket identifier, title, maybe worktree path)
- record launch event
- optionally register resulting session if practical

### Important
Simple and opinionated is fine for MVP.

### Done when
- backend can launch a new agent command locally from a ticket

---

## Task 11.3: Launch endpoint and UI button
Implement:
- API endpoint to launch for a ticket
- UI button next to ticket row

### Done when
- clicking a ticket can start a new agent workflow

---

## Task 11.4: `/work` skill compatibility
If practical, include an initial template that assumes the user has a standard workflow prompt/skill under something like `/work`.

This can be done by:
- configurable prompt file path
- injecting ticket identifier/title into the command

### Done when
- launcher is compatible with the user’s intended standard ticket workflow

---

# Phase 12 — Polish and Reliability

## Task 12.1: Better stale session handling
Implement logic or indicators for:
- sessions with old heartbeats
- sessions that look dead
- ended sessions

### Done when
- UI can distinguish fresh vs stale activity

---

## Task 12.2: Better lease warnings
Add UI and API visibility for:
- expired leases
- near-expiry countdown
- owner last heartbeat

### Done when
- humans can understand lease health quickly

---

## Task 12.3: Error handling and response consistency
Ensure API returns:
- clear error shapes
- helpful messages
- machine-readable codes if practical

### Done when
- CLI and UI can present errors cleanly

---

## Task 12.4: README installation and usage
Document:
- install steps
- local setup
- running backend/frontend
- using CLI
- using launcher
- connecting Linear

### Done when
- repo is usable by an external developer

---

## Task 12.5: Sample config
Add:
- sample `.env`
- sample launcher template config
- example commands

### Done when
- new users can bootstrap quickly

---

# Phase 13 — Testing

## Task 13.1: Backend unit tests
Cover:
- sessions
- leases
- queue
- messages
- ticket import mapping if practical

### Done when
- core logic has good test coverage

---

## Task 13.2: API tests
Cover:
- register session
- acquire lease
- queue enqueue
- post message
- list dashboard-relevant data

### Done when
- main API contract works end-to-end

---

## Task 13.3: CLI smoke tests
At least verify:
- CLI can hit local API
- common commands work
- JSON output is valid

### Done when
- terminal UX is not fragile

---

## Task 13.4: Manual multi-agent scenario
Run and document a test scenario with two fake or real sessions:

1. create session A
2. create session B
3. A acquires `shared-dev`
4. B queues
5. A heartbeats
6. A releases
7. B acquires
8. both post status and messages
9. UI reflects transitions

### Done when
- this scenario works reliably

---

# Phase 14 — Nice-to-Haves If Easy

Only do these if the core is already working well.

## Optional 14.1
Add commit SHA to lease display and CLI.

## Optional 14.2
Auto-detect current git branch/worktree in CLI register command.

## Optional 14.3
Support per-ticket channels automatically in messages view.

## Optional 14.4
Add simple filtering/search in sessions and tickets UI.

## Optional 14.5
Add SSE or websockets for live UI updates.
Polling is acceptable first.

---

## 4. Suggested Initial Milestone Plan

### Milestone A — Core coordination
Build:
- DB
- sessions
- leases
- queue
- CLI
- tests

Goal:
A terminal-only user can safely coordinate shared-dev.

---

### Milestone B — Visibility
Build:
- dashboard
- sessions view
- lease view
- queue view
- events

Goal:
A human can open localhost and see what is happening.

---

### Milestone C — Collaboration
Build:
- messages/common area
- tickets model
- Linear import
- tickets view

Goal:
Humans and agents can coordinate with shared context.

---

### Milestone D — Launch from ticket
Build:
- launcher config
- launch endpoint
- UI launch button

Goal:
A user can click a ticket and start a new agent workflow.

---

## 5. Required Design Decisions To Record

As implementation proceeds, record answers to these in `docs/decisions.md`:

- Python dependency/tooling choice
- ORM choice
- migration strategy
- lease constraint implementation strategy in SQLite
- queue policy
- UI polling interval
- launcher implementation approach
- Linear import approach
- CLI packaging/install story

---

## 6. Final Build Instruction

Build the smallest real version of Coordinaut that I can use locally with multiple coding agents.

It must include:
- local persistent coordination state
- session tracking
- queue + lease semantics for `shared-dev`
- shared messages/context
- localhost UI
- ticket display
- launch-agent-from-ticket flow

Prefer a boring, robust implementation over a clever one.

When unsure, bias toward:
- SQLite
- FastAPI
- Typer
- React
- simple polling
- shell-based launcher
- clear event logging