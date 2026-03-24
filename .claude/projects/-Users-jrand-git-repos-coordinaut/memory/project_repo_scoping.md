---
name: repo-scoping-architecture
description: Repos are a first-class scoping concept — resources are repo-scoped, tickets are not
type: project
---

Repos are a first-class entity that scope most data objects. Key decisions:

- **Resources/envs are repo-scoped** — each repo gets its own `shared-dev` resource and lease queue
- **Tickets are NOT repo-scoped** — they can span repos (Linear projects don't map 1:1 to repos)
- Sessions, leases, queue entries, messages, workflow events should be repo-scoped
- The Repos page was added post-spec and needs to be reflected in SPEC.md
- User must select a target repo to segment the UI views

**Why:** Multiple repos may share a Coordinaut instance, but each has its own shared dev environment. Tickets (from Linear) are cross-cutting.

**How to apply:** All new features and data models should consider repo scoping. UI views (except Tickets) should filter by selected repo.
