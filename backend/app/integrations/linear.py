"""Linear integration for ticket import."""

from __future__ import annotations

import json

import httpx
from fastapi import HTTPException
from sqlalchemy.orm import Session

from app.config import settings
from app.models.ticket import Ticket
from app.services.event_service import log_event

LINEAR_API_URL = "https://api.linear.app/graphql"

TEAMS_QUERY = """
query {
  teams {
    nodes {
      id
      name
      key
    }
  }
}
"""

ISSUES_QUERY = """
query TeamIssues($teamId: String!, $first: Int) {
  team(id: $teamId) {
    issues(first: $first, orderBy: updatedAt) {
      nodes {
        id
        identifier
        title
        description
        priority
        url
        state { name }
        assignee { name }
        labels { nodes { name } }
      }
    }
  }
}
"""

MY_ISSUES_QUERY = """
query MyIssues($first: Int) {
  issues(first: $first, orderBy: updatedAt) {
    nodes {
      id
      identifier
      title
      description
      priority
      url
      team { id name key }
      state { name }
      assignee { name }
      labels { nodes { name } }
    }
  }
}
"""


def _headers() -> dict:
    return {"Authorization": settings.linear_api_key, "Content-Type": "application/json"}


def _graphql(query: str, variables: dict | None = None) -> dict:
    try:
        resp = httpx.post(
            LINEAR_API_URL,
            headers=_headers(),
            json={"query": query, "variables": variables or {}},
            timeout=30,
        )
        resp.raise_for_status()
        data = resp.json()
        if "errors" in data:
            raise HTTPException(status_code=502, detail=f"Linear GraphQL errors: {data['errors']}")
        return data
    except httpx.HTTPError as e:
        raise HTTPException(status_code=502, detail=f"Linear API error: {e}")


def get_linear_teams() -> list[dict]:
    """Fetch available Linear teams."""
    if not settings.linear_api_key:
        raise HTTPException(status_code=400, detail="COORDINAUT_LINEAR_API_KEY not configured")
    data = _graphql(TEAMS_QUERY)
    return data.get("data", {}).get("teams", {}).get("nodes", [])


def import_linear_tickets(db: Session, team_id: str | None = None) -> list[Ticket]:
    if not settings.linear_api_key:
        raise HTTPException(
            status_code=400,
            detail="COORDINAUT_LINEAR_API_KEY not configured. Set it in .env",
        )

    target_team_id = team_id or settings.linear_team_id

    if target_team_id:
        # Fetch by team
        data = _graphql(ISSUES_QUERY, {"teamId": target_team_id, "first": 50})
        issues = data.get("data", {}).get("team", {}).get("issues", {}).get("nodes", [])
    else:
        # No team specified — fetch all issues visible to the API key
        data = _graphql(MY_ISSUES_QUERY, {"first": 50})
        issues = data.get("data", {}).get("issues", {}).get("nodes", [])

    tickets = []
    for issue in issues:
        labels = [l["name"] for l in issue.get("labels", {}).get("nodes", [])]
        existing = db.query(Ticket).filter(Ticket.identifier == issue["identifier"]).first()

        fields = dict(
            title=issue["title"],
            description=issue.get("description"),
            state=issue.get("state", {}).get("name", "unknown"),
            priority=issue.get("priority"),
            assignee=issue.get("assignee", {}).get("name") if issue.get("assignee") else None,
            labels_json=json.dumps(labels) if labels else None,
            url=issue.get("url"),
            external_id=issue["id"],
            source="linear",
        )

        if existing:
            for k, v in fields.items():
                setattr(existing, k, v)
            tickets.append(existing)
        else:
            ticket = Ticket(identifier=issue["identifier"], **fields)
            db.add(ticket)
            tickets.append(ticket)

    log_event(db, "linear_sync", f"Imported {len(tickets)} tickets from Linear")
    db.commit()
    for t in tickets:
        db.refresh(t)
    return tickets
