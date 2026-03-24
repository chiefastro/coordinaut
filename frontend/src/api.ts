const BASE = '/api';

async function request<T>(path: string, options?: RequestInit): Promise<T> {
  const resp = await fetch(`${BASE}${path}`, {
    headers: { 'Content-Type': 'application/json' },
    ...options,
  });
  if (!resp.ok) {
    const err = await resp.json().catch(() => ({ detail: resp.statusText }));
    throw new Error(err.detail || resp.statusText);
  }
  return resp.json();
}

export const api = {
  health: () => request<{ status: string; version: string }>('/health'),

  // Sessions
  listSessions: (activeOnly = false) =>
    request<any[]>(`/sessions?active_only=${activeOnly}`),
  registerSession: (data: any) =>
    request<any>('/sessions/register', { method: 'POST', body: JSON.stringify(data) }),
  endSession: (id: string) =>
    request<any>(`/sessions/${id}/end`, { method: 'POST' }),

  // Leases
  getActiveLeases: () => request<any[]>('/leases/active'),
  getLeaseHistory: (limit = 20) => request<any[]>(`/leases/history?limit=${limit}`),
  getResourceLease: (key: string) => request<any | null>(`/leases/resource/${key}`),
  releaseLease: (data: { resource_key: string; session_id: string; release_reason?: string }) =>
    request<any>('/leases/release', { method: 'POST', body: JSON.stringify(data) }),

  // Queue
  listQueue: () => request<any[]>('/queue'),
  listResourceQueue: (key: string) => request<any[]>(`/queue/${key}`),

  // Messages
  listMessages: (limit = 100) => request<any[]>(`/messages?limit=${limit}`),
  listChannelMessages: (channel: string, limit = 100) =>
    request<any[]>(`/messages/channel/${channel}?limit=${limit}`),
  postMessage: (data: any) =>
    request<any>('/messages', { method: 'POST', body: JSON.stringify(data) }),

  // Events
  listEvents: (limit = 50) => request<any[]>(`/events?limit=${limit}`),

  // Tickets
  listTickets: () => request<any[]>('/tickets'),
  importLinear: () => request<any[]>('/tickets/import/linear', { method: 'POST' }),

  // Resources
  listResources: () => request<any[]>('/resources'),

  // Launcher
  launchAgent: (data: { ticket_identifier: string; template_name?: string }) =>
    request<any>('/launch/agent', { method: 'POST', body: JSON.stringify(data) }),
  getTemplates: () => request<any>('/launch/templates'),

  // Repos
  listRepos: () => request<any[]>('/repos'),
  discoverSessions: () => request<any[]>('/repos/sessions'),

  // Linear teams
  getLinearTeams: () => request<any[]>('/tickets/linear/teams'),
};
