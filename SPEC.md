# Coordinaut MVP Spec
Version: 0.1
Status: Planning
Repo: coordinaut
Primary goal: Build an open-source local-first MVP that coordinates multiple coding agents working against a shared development environment.

---

## 1. Product Summary

Coordinaut is a local-first coordination layer for autonomous coding workflows.

It provides:

- a local persistent system of record for environment leases
- a local API that coding agents can call
- a CLI for agent and human convenience
- a localhost web UI showing agent sessions, tickets, worktrees, queue state, lease ownership, and shared context
- a lightweight shared messaging/context layer between agents
- an optional ticket-driven launcher flow that can start a new agent for a Linear issue and apply a standard workflow

The first version is intentionally single-user / single-machine oriented, but should be designed so the architecture can later support a hosted multi-user control plane.

---

## 2. Problem Statement

When multiple coding agents operate in parallel on the same codebase, they often share one mutable development environment for final deploy and verification.

This causes a coordination failure:

- Agent A deploys to shared dev
- Agent B deploys before Agent A finishes validation
- Agent A now believes it is testing its own deployment, but it is not
- Validation becomes untrustworthy
- Human supervision becomes costly and confusing

Traditional CI/CD tools do not fully solve this because the critical section is not just deploy. It is:

1. acquire access to shared env
2. deploy exact code/config
3. verify deployed fingerprint
4. run validation
5. release access

Coordinaut is meant to be the local system of record for that workflow.

---

## 3. Design Principles

### Local-first
The open-source MVP must run entirely on a local developer machine.

### Persistent
State must survive restarts.

### Agent-friendly
Everything important must be accessible via API and CLI, not just UI.

### Human-visible
Humans must be able to open localhost and immediately understand:
- what agents exist
- what they are working on
- who owns shared dev
- who is waiting
- what happened recently

### Minimal dependencies
Keep setup simple. The local OSS version should not require cloud infra.

### Evolvable
Internal abstractions should support a future hosted SaaS version.

---

## 4. MVP Goals

The MVP should support the following end-to-end flow:

1. Human views a list of Linear tickets in the UI
2. Human clicks a button to start a new coding agent for a given ticket
3. The agent session is registered in Coordinaut
4. The agent reports its current state as it works
5. When ready for shared dev, the agent enqueues for deployment/verification
6. Coordinaut grants the lease when available
7. The agent performs deploy + verification while heartbeating its lease
8. The agent releases the lease
9. Humans can inspect the entire process in the UI
10. Agents can leave shared notes/messages/context for each other

---

## 5. Non-Goals for MVP

These are explicitly out of scope for the first version unless easy to add:

- hosted multi-user cloud service
- production-grade auth and org management
- distributed multi-machine coordination
- advanced fairness / priority policies
- deep IDE/editor integration
- generic plugin platform
- full CI/CD replacement
- preview environment creation
- durable agent execution engine
- production deployment coordination

---

## 6. Target Users

### Primary
A solo developer or small team running multiple coding agents locally or semi-locally, especially with:
- Claude Code
- Codex-style agents
- worktrees
- Linear-based workflows
- one shared mutable dev environment

### First customer
The repo owner using this for real development against their own complex AWS shared dev stack.

---

## 7. Core Concepts

### Repository
A git repository that the user is coordinating agent work against. Repositories are a first-class scoping entity — most other concepts (resources, sessions, leases, queues, messages, events) are scoped to a repository. The user selects an active repository in the UI, and all views filter accordingly.

Repositories are discovered from configured target paths and inspected for git metadata (branches, worktrees, remotes, recent commits).

### Resource
A shared mutable thing that must be coordinated. Resources are **repo-scoped** — each repository has its own set of resources (e.g., each repo has its own `shared-dev`).

Examples:
- `shared-dev`
- `staging-db-migration-window`
- `integration-test-env`

MVP can start with one canonical resource per repo: `shared-dev`.

### Lease
A temporary exclusive claim over a resource.
A lease has:
- owner session
- ticket
- TTL
- heartbeat
- status

### Queue
A list of sessions waiting for access to a resource.

### Session
A running coding agent instance. Sessions are scoped to a repository.
Examples:
- Claude Code session in a terminal
- Codex process
- future remote agent

### Worktree
The git worktree associated with a session.

### Ticket
Usually a Linear issue, but should be abstracted so it is not permanently coupled to Linear. Tickets are **not repo-scoped** — they can span repositories, since a Linear project may not map 1:1 to a single repo.

### Shared Context / Common Area
A place where agents and humans can post messages, notes, or handoff context. Messages are scoped to a repository (via channels like `#common`, `#resource/shared-dev`) or to a ticket (via `#ticket/ABC-123`, which is cross-repo).

### Workflow Status
A normalized state machine representing where the agent is in the dev workflow.

---

## 8. Recommended Tech Stack

### Backend API
- Python
- FastAPI

Reason:
- quick to build
- good CLI + API ecosystem
- aligns well with coding-agent-friendly tooling
- good local packaging story

### Local persistent store
- SQLite as the default system of record

Reason:
- zero-config
- persistent
- queryable
- transactional
- suitable for local single-user coordination
- easier than file-only design for queueing and leases

### Frontend
- React + TypeScript + Vite
- simple component library or minimal custom UI
- no premature complexity

### CLI
- Python Typer or Click

### Process management for local agent launcher
- start simple with shell command execution from backend or CLI
- abstract so later it can support pluggable agent launchers

### ORM / DB layer
- SQLAlchemy or SQLModel
- Alembic for migrations if needed

### Real-time UI updates
Start with polling.
Later:
- websocket or Server-Sent Events

---

## 9. Architecture Overview

### Local architecture
Single machine app with:

- SQLite database
- FastAPI server
- web UI
- CLI client
- optional local agent launcher
- optional Linear sync module

### Components

#### 1. API server
Responsible for:
- leases
- queue
- sessions
- ticket records
- messages
- workflow state transitions

#### 2. CLI
Responsible for:
- session registration
- status updates
- queue / lease operations
- messaging
- convenience commands

#### 3. UI
Responsible for:
- dashboards
- session monitoring
- ticket view
- queue / lease view
- common-area messaging
- admin config

#### 4. Integrations layer
Initially:
- Linear read/sync
- local shell-based agent launch

Later:
- GitHub
- Claude Code deeper hooks
- cloud mode

---

## 10. SQLite Recommendation

Use SQLite, not flat files, as the primary persistent store.

### Why SQLite
- supports atomic updates for lease acquisition
- avoids race-prone hand-rolled file locking
- easy to inspect manually
- supports tables, indexes, and queries needed for dashboards
- can still store JSON blobs for flexible event payloads

### Where files may still be useful
Optional secondary use cases:
- storing raw logs
- attaching longer message content
- export/import snapshots

But files should not be the source of truth for leases.

---

## 11. Data Model

The following schema is recommended for MVP.

### repositories
Represents a git repository that Coordinaut coordinates work against. This is the primary scoping entity for most other tables.

Fields:
- `id` (string/uuid primary key)
- `key` unique (short slug, e.g. `skillenai-ds`)
- `name` (display name)
- `path` (absolute local path)
- `remote_url` nullable
- `default_branch` nullable
- `is_active` default true
- `metadata_json`
- `created_at`
- `updated_at`

### sessions
Represents running agent sessions. **Repo-scoped.**

Fields:
- `id` (string/uuid primary key)
- `repo_id` (FK to repositories)
- `agent_type` (`claude_code`, `codex`, `manual`, etc.)
- `display_name`
- `pid` nullable
- `host` default `localhost`
- `worktree_path`
- `branch_name`
- `ticket_id` nullable
- `status`
- `started_at`
- `last_seen_at`
- `ended_at` nullable
- `metadata_json`

### tickets
Represents work items, usually synced from Linear. **Not repo-scoped** — tickets can span repositories.

Fields:
- `id` (internal primary key)
- `external_id` (e.g. Linear issue id)
- `identifier` (e.g. `ABC-123`)
- `title`
- `description` nullable
- `state`
- `priority` nullable
- `assignee` nullable
- `labels_json`
- `url` nullable
- `source` (`linear`, `manual`)
- `synced_at`
- `metadata_json`

### resources
Represents shared environments / lockable resources. **Repo-scoped** — each repository has its own set of resources.

Fields:
- `id`
- `repo_id` (FK to repositories)
- `key` (e.g. `shared-dev`, unique per repo)
- `name`
- `description`
- `lease_ttl_seconds`
- `is_enabled`
- `metadata_json`

Constraint:
- unique(`repo_id`, `key`)

### leases
Represents current or historical lease records. Scoped to a resource (which is repo-scoped).

Fields:
- `id`
- `resource_key`
- `repo_id` (FK to repositories)
- `session_id`
- `ticket_identifier` nullable
- `commit_sha` nullable
- `state` (`active`, `released`, `expired`, `cancelled`, `failed`)
- `acquired_at`
- `expires_at`
- `heartbeat_at`
- `released_at` nullable
- `release_reason` nullable
- `metadata_json`

Constraint:
- at most one active lease per resource per repo

### queue_entries
Represents waitlist for a resource. Scoped to a resource (which is repo-scoped).

Fields:
- `id`
- `resource_key`
- `repo_id` (FK to repositories)
- `session_id`
- `ticket_identifier` nullable
- `priority` default 0
- `state` (`queued`, `granted`, `cancelled`, `expired`, `done`)
- `requested_at`
- `granted_at` nullable
- `completed_at` nullable
- `metadata_json`

### workflow_events
Append-only event log. **Repo-scoped.**

Fields:
- `id`
- `repo_id` (FK to repositories) nullable
- `timestamp`
- `session_id` nullable
- `ticket_identifier` nullable
- `resource_key` nullable
- `event_type`
- `message`
- `payload_json`

### messages
Shared common-area messages. **Repo-scoped** — channels like `#common` and `#resource/*` are per-repo. Ticket channels (`#ticket/ABC-123`) are cross-repo.

Fields:
- `id`
- `repo_id` (FK to repositories) nullable
- `channel` default `common`
- `author_type` (`agent`, `human`, `system`)
- `author_name`
- `session_id` nullable
- `ticket_identifier` nullable
- `message`
- `created_at`
- `metadata_json`

### status_updates
Normalized session workflow status history.

Fields:
- `id`
- `session_id`
- `status`
- `summary` nullable
- `created_at`
- `metadata_json`

### app_config
Key-value config store.

Fields:
- `key`
- `value_json`
- `updated_at`

---

## 12. Canonical Workflow Statuses

Use a normalized set of statuses for the MVP UI.

Recommended enum values:

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

Agents should be allowed to post status updates with a summary message.

---

## 13. Lease Semantics

This is the core of the app.

### Lease acquisition rules
A session may acquire a lease for a resource only if:
- the resource has no active unexpired lease
- or the active lease is expired and can be taken over safely

### Heartbeat rules
A session holding a lease must periodically heartbeat before expiration.

### Lease expiration
If a lease is not heartbeated before TTL, it becomes expired and the resource becomes available.

### Critical section
The lease must be held across the full shared-env phase:
- deploy
- deploy completion
- verification
- release

### Queue interaction
If the resource is unavailable:
- session may enqueue
- queue order is visible
- a grant operation should promote the next eligible queued session

### MVP simplification
For MVP, queue order can be FIFO with optional static priority.

---

## 14. API Spec (MVP)

All endpoints are local-first and run on localhost.

Repo-scoped endpoints accept a `repo_id` query parameter or include it in the request body. Ticket endpoints are not repo-scoped.

### Health
- `GET /health`

### Repositories
- `GET /repos` — list all registered repositories with git metadata
- `POST /repos` — register a new repository
- `GET /repos/{repo_id}` — get repository details
- `PATCH /repos/{repo_id}` — update repository settings
- `GET /repos/sessions` — discover running Claude Code processes

### Sessions (repo-scoped)
- `POST /sessions/register` — body includes `repo_id`
- `POST /sessions/{session_id}/heartbeat`
- `POST /sessions/{session_id}/status`
- `POST /sessions/{session_id}/end`
- `GET /sessions?repo_id={repo_id}`
- `GET /sessions/{session_id}`

### Tickets (not repo-scoped)
- `GET /tickets`
- `POST /tickets/import/linear`
- `POST /tickets`
- `GET /tickets/{identifier}`

### Resources (repo-scoped)
- `GET /resources?repo_id={repo_id}`
- `POST /resources` — body includes `repo_id`
- `PATCH /resources/{key}?repo_id={repo_id}`

### Queue (repo-scoped)
- `POST /queue/enqueue` — body includes `repo_id`
- `POST /queue/{entry_id}/cancel`
- `GET /queue?repo_id={repo_id}`
- `GET /queue/{resource_key}?repo_id={repo_id}`

### Leases (repo-scoped)
- `POST /leases/acquire` — body includes `repo_id`
- `POST /leases/heartbeat`
- `POST /leases/release`
- `GET /leases/active?repo_id={repo_id}`
- `GET /leases/history?repo_id={repo_id}`
- `GET /leases/resource/{resource_key}?repo_id={repo_id}`

### Messages (repo-scoped for repo channels, cross-repo for ticket channels)
- `GET /messages?repo_id={repo_id}`
- `POST /messages` — body includes `repo_id` (nullable for ticket channels)
- `GET /messages/channel/{channel}?repo_id={repo_id}`

### Events (repo-scoped)
- `GET /events?repo_id={repo_id}`
- `POST /events` — body includes `repo_id`

### Launcher
- `POST /launch/agent` — body includes `repo_id`
- `GET /launch/templates`

### Config
- `GET /config`
- `PATCH /config`

---

## 15. CLI Spec (MVP)

Binary name:
- `coordinaut`

### Repo commands
- `coordinaut repo list`
- `coordinaut repo add <path>`
- `coordinaut repo info <repo_id>`
- `coordinaut repo select <repo_id>` — set active repo for subsequent commands

### Session commands (repo-scoped)
- `coordinaut session register --repo <repo_id>`
- `coordinaut session heartbeat`
- `coordinaut session status`
- `coordinaut session end`
- `coordinaut session list`

### Queue commands (repo-scoped)
- `coordinaut queue enqueue`
- `coordinaut queue cancel`
- `coordinaut queue list`

### Lease commands (repo-scoped)
- `coordinaut lease acquire`
- `coordinaut lease heartbeat`
- `coordinaut lease release`
- `coordinaut lease status`

### Message commands (repo-scoped)
- `coordinaut msg post`
- `coordinaut msg list`

### Ticket commands (not repo-scoped)
- `coordinaut ticket list`
- `coordinaut ticket import-linear`

### Launch commands
- `coordinaut launch agent --ticket ABC-123 --repo <repo_id>`
- `coordinaut launch agent --ticket ABC-123 --template work-skill`

### Serve commands
- `coordinaut serve`
- `coordinaut ui`

### Init commands
- `coordinaut init`

### Suggested global flags
- `--api-url`
- `--repo` — target repository (can also be inferred from cwd)
- `--session-id`
- `--json`
- `--quiet`

---

## 16. Agent Protocol

This should be documented and used consistently.

### Agent startup
When a new agent begins work:
1. register session
2. attach ticket
3. attach worktree path / branch
4. set status to `local_dev`

### Shared env phase
When ready for shared dev:
1. enqueue for `shared-dev`
2. set status `shared_env_enqueued`
3. attempt or wait for lease
4. once lease acquired, set status `shared_env_lease_acquired`
5. deploy and set `shared_env_deploy_running`
6. when deploy ends, set `shared_env_deploy_complete`
7. perform verification, set `shared_env_verification`
8. release lease, set `shared_env_released`

### Agent notes
Agents should post context such as:
- assumptions
- blockers
- findings
- handoff notes
- important repo observations

---

## 17. Web UI Requirements

The local UI should be available in the browser on localhost.

### Repo selector
The UI should include a persistent repo selector (e.g., in the header or sidebar). The user selects an active repository, and all repo-scoped views (Dashboard, Sessions, Queue, Leases, Messages, Events) filter to that repo. Tickets are not filtered by repo.

### Repos view
Display:
- list of registered repositories with git metadata
- for each repo: name, path, remote URL, default branch, dirty file count
- worktrees table (path, branch, HEAD)
- branches table (name, upstream)
- recent commits (hash, message, author, time)
- discovered Claude Code processes and their working directories

### Main dashboard (repo-scoped)
Display:
- active sessions count (for selected repo)
- active lease owner for `shared-dev` (for selected repo)
- queue length (for selected repo)
- recent events (for selected repo)
- tickets in progress
- tickets waiting for shared env
- expired lease warnings

### Sessions view (repo-scoped)
Table columns:
- session
- agent type
- worktree
- branch
- ticket
- current status
- started
- last heartbeat
- actions

### Queue view (repo-scoped)
Table columns:
- position
- resource
- session
- ticket
- requested at
- priority
- status

### Lease view (repo-scoped)
Display:
- active resource owner
- lease countdown
- commit sha if known
- history table

### Tickets view (not repo-scoped)
Display:
- Linear ticket list
- state
- labels
- assignee
- “launch agent” button

### Common area / messages (repo-scoped for repo channels)
Display:
- shared messages from humans and agents
- channels such as:
  - `common` (repo-scoped)
  - `ticket/ABC-123` (cross-repo)
  - `resource/shared-dev` (repo-scoped)

### Events view (repo-scoped)
Display:
- append-only event log for the selected repo
- event type, timestamp, session, message
- filterable by event type

### Admin / config view
Manage:
- resource definitions (per repo)
- lease TTL
- launcher templates
- Linear API config
- default paths and commands

---

## 18. Linear Integration MVP

Linear integration should be useful but not block the whole app.

### MVP functionality
- fetch tickets from Linear
- display tickets in the UI
- optionally cache / sync into local DB
- allow launching an agent for a ticket

### Optional later features
- push status back to Linear
- create comments
- map Coordinaut statuses to Linear workflow states

### Important
Linear should be an integration, not a foundational dependency.
Tickets should be representable without Linear.

---

## 19. Agent Launcher Design

The launcher is a high-value feature.

### Goal
Click a button next to a ticket and start an agent on a standard workflow.

### MVP design
Define launch templates in config.
A template includes:
- command to run
- working directory
- worktree strategy
- arguments
- environment variables
- optional skill / prompt file path

Example conceptual template:
- agent type: Claude Code
- create/select worktree for ticket
- open terminal or spawn process
- pass a standard instruction workflow from `/work`

### MVP limitations
It is okay if the first launcher:
- only works on macOS/Linux
- only supports a simple shell command
- expects certain local tool conventions

The feature is still worthwhile even if initially opinionated.

---

## 20. Shared Context / Messaging Design

This is not just chat. It is structured lightweight coordination.

### Use cases
- Agent A tells Agent B what it learned
- Human adds guidance for all sessions
- Human posts repo-wide context
- Agent leaves a handoff note
- Agents ask for human attention

### MVP message model
Simple messages with:
- channel
- author
- body
- timestamp
- optional links to ticket/session/resource

### Suggested channels
- `common`
- `ticket/<identifier>`
- `resource/<resource_key>`
- `session/<session_id>`

### Future extension
Later, messages can become richer:
- pinned notes
- task checklists
- artifacts
- references to files / commits / PRs

---

## 21. UX Expectations

### Human experience
The human should be able to:
- open localhost and understand what is happening within seconds
- see whether shared dev is safe to use
- launch a new agent from a ticket
- inspect messages and recent events
- resolve confusion without digging through terminal logs

### Agent experience
The agent should be able to:
- make a few simple CLI calls
- not reason about coordination details itself
- rely on Coordinaut as the source of truth

---

## 22. Suggested Repo Structure

Suggested initial structure:

/backend
  /app
    /api
    /models
    /services
    /db
    /integrations
    /launcher
    /schemas
  pyproject.toml

/frontend
  /src

/cli
  /coordinaut_cli

/docs
  mvp_spec.md

/scripts

This may also be reorganized into a monorepo with one Python package and one frontend package.

A simpler alternative:
- keep API + CLI in one Python package
- keep UI separate

---

## 23. Suggested Service Layer Responsibilities

### Lease service
- acquire lease atomically
- heartbeat lease
- release lease
- expire stale leases
- fetch current lease state

### Queue service
- enqueue
- cancel
- list queue
- grant next
- maintain ordering

### Session service
- register
- update heartbeats
- set status
- end session

### Ticket service
- sync from Linear
- store / query tickets

### Message service
- post / list messages

### Launcher service
- run launch templates
- register resulting session if applicable

### Event service
- append and query event log

---

## 24. Concurrency Notes

Because SQLite is local and the MVP is single-machine oriented, this is acceptable.
Still, lease acquisition must be implemented carefully.

### Requirements
- atomic acquisition
- no split-brain lease states
- stale lease cleanup before acquisition
- queue grant should not violate active lease constraints

### Practical guidance
Implement lease acquisition in a transaction.

If using SQLite:
- enable WAL mode if helpful
- keep write transactions short
- use DB constraints to enforce one active lease per resource

---

## 25. Security Model for MVP

For local OSS version:
- default to no auth on localhost
- optionally support a local API token
- assume single-user trusted environment

This is acceptable for MVP.
Do not overengineer auth yet.

For future cloud version:
- team auth
- API keys
- org/workspace separation
- RBAC

---

## 26. Packaging and Distribution

### Open-source local version
Should be easy to install with:
- `pipx install ...`
or
- Homebrew later
or
- Docker optional, but not required

### Desired setup flow
1. install coordinaut
2. run `coordinaut init`
3. run `coordinaut serve`
4. open localhost UI
5. connect Linear optionally
6. start registering agent sessions

---

## 27. MVP Milestones

### Milestone 1: Local core
Build:
- SQLite schema
- FastAPI API
- session registration
- basic lease acquire/release/heartbeat
- basic queue
- CLI commands

Definition of done:
A human and one or more scripts can coordinate access to `shared-dev`.

### Milestone 2: Visibility
Build:
- event log
- sessions UI
- lease UI
- queue UI

Definition of done:
Open localhost and see active coordination state.

### Milestone 3: Tickets + launch
Build:
- Linear import
- tickets UI
- launch button
- configurable launcher template

Definition of done:
A user can click a ticket and start a new agent workflow.

### Milestone 4: Shared context
Build:
- common-area messages
- ticket/resource channels
- simple posting from CLI and UI

Definition of done:
Agents and humans can leave coordination notes.

### Milestone 5: Hardening
Build:
- better stale session handling
- better lease expiration behavior
- tests
- packaging
- docs

Definition of done:
Usable for real daily development.

---

## 28. Recommended First Deliverables for the Coding Agent

The coding agent should implement in this order:

1. project skeleton
2. SQLite schema and migrations
3. FastAPI endpoints for sessions, queue, leases
4. CLI wrappers for session + queue + lease commands
5. basic tests for lease semantics
6. simple frontend dashboard
7. Linear read integration
8. launcher framework
9. shared messages UI and API
10. polish and docs

---

## 29. Testing Requirements

### Backend tests
Must test:
- lease acquisition on empty resource
- lease acquisition while active lease exists
- lease expiration
- heartbeat extending lease
- queue ordering
- release behavior
- session registration / status updates

### Integration tests
Must test:
- CLI calling local API
- UI reflecting backend state
- launch flow creating session records

### Manual test scenario
Simulate:
- two fake agent sessions
- both targeting `shared-dev`
- first gets lease
- second queues
- first heartbeats, then releases
- second acquires
- UI reflects each transition

---

## 30. Observability Requirements

MVP should at least expose:
- recent events
- session last-seen timestamps
- lease TTL countdown
- resource state

Do not overbuild metrics initially.

---

## 31. Future SaaS Path

The architecture should support a future freemium hosted version.

### Free OSS local mode
- SQLite
- localhost
- single developer
- optional integrations
- no auth

### Pro hosted version
- cloud API
- managed persistent store
- shared team workspace
- remote agents
- hosted dashboards
- audit history
- richer policy controls

Design implication:
Keep persistence and config abstractions clean enough that SQLite can later be swapped for Postgres.

---

## 32. Positioning Notes

Coordinaut should not be positioned as just a lock service.

It is:
- a local control plane for multi-agent development workflows
- a coordination layer for shared mutable dev environments
- a visibility surface for agent sessions, tickets, and shared-env ownership

This matters for product direction and UX decisions.

---

## 33. Open Questions

The coding agent may make reasonable decisions on these, but should document them:

- exact launcher implementation strategy
- whether session registration is manual or auto-wrapped
- whether queue grant is automatic or explicit
- whether UI uses polling or SSE initially
- how much Linear data to cache
- whether worktree detection is manual or inferred from cwd

---

## 34. Implementation Preferences

When in doubt, optimize for:
- simplicity
- usability
- local reliability
- inspectability
- future extensibility

Avoid:
- premature distributed systems complexity
- over-designed auth
- abstract plugin systems before real need
- premature multi-tenant assumptions in the OSS local version

---

## 35. Immediate Build Request

Build the OSS local-first MVP of Coordinaut with the following minimum usable path:

- local FastAPI server
- SQLite persistence
- CLI for sessions, leases, queue, messages
- web UI on localhost
- one resource called `shared-dev`
- session tracking for Claude Code / Codex agents
- ability to associate session with:
  - worktree
  - branch
  - Linear ticket
  - workflow status
- queue + lease semantics for `shared-dev`
- common-area messaging
- Linear ticket list in UI
- button to launch an agent on a ticket through a configurable shell-based template

The implementation should be practical and biased toward working software over abstract architecture.