export interface Session {
  id: string;
  agent_type: string;
  display_name: string;
  pid: number | null;
  host: string;
  worktree_path: string | null;
  branch_name: string | null;
  repo_path: string | null;
  ticket_id: string | null;
  status: string;
  started_at: string;
  last_seen_at: string;
  ended_at: string | null;
  metadata_json: string | null;
}

export interface Lease {
  id: string;
  resource_key: string;
  session_id: string;
  ticket_identifier: string | null;
  commit_sha: string | null;
  state: string;
  acquired_at: string;
  expires_at: string;
  heartbeat_at: string;
  released_at: string | null;
  release_reason: string | null;
  metadata_json: string | null;
}

export interface QueueEntry {
  id: string;
  resource_key: string;
  session_id: string;
  ticket_identifier: string | null;
  priority: number;
  state: string;
  requested_at: string;
  granted_at: string | null;
  completed_at: string | null;
  metadata_json: string | null;
}

export interface Message {
  id: string;
  channel: string;
  author_type: string;
  author_name: string;
  session_id: string | null;
  ticket_identifier: string | null;
  message: string;
  created_at: string;
  metadata_json: string | null;
}

export interface WorkflowEvent {
  id: string;
  timestamp: string;
  session_id: string | null;
  ticket_identifier: string | null;
  resource_key: string | null;
  event_type: string;
  message: string;
  payload_json: string | null;
}

export interface Resource {
  id: string;
  key: string;
  name: string;
  description: string;
  lease_ttl_seconds: number;
  is_enabled: boolean;
  metadata_json: string | null;
}

export interface Ticket {
  id: string;
  external_id: string | null;
  identifier: string;
  title: string;
  description: string | null;
  state: string;
  priority: number | null;
  assignee: string | null;
  labels_json: string | null;
  url: string | null;
  source: string;
  synced_at: string;
  metadata_json: string | null;
}
