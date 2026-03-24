import { useCallback } from 'react';
import { api } from '../api';
import { usePolling, timeAgo } from '../hooks';
import type { Session } from '../types';

export default function Sessions() {
  const { data: sessions, refresh } = usePolling<Session[]>(
    useCallback(() => api.listSessions(), []), 5000
  );

  const handleEnd = async (id: string) => {
    try {
      await api.endSession(id);
      refresh();
    } catch (e: any) {
      alert(e.message);
    }
  };

  const statusBadge = (status: string) => {
    if (status === 'completed' || status === 'shared_env_released') return 'green';
    if (status === 'failed' || status === 'cancelled') return 'red';
    if (status.startsWith('shared_env')) return 'yellow';
    if (status === 'blocked') return 'red';
    if (status === 'idle') return 'idle';
    return 'blue';
  };

  return (
    <div>
      <h2>Sessions</h2>
      {sessions && sessions.length > 0 ? (
        <table>
          <thead>
            <tr>
              <th>ID</th><th>Name</th><th>Agent</th><th>Branch</th>
              <th>Ticket</th><th>Status</th><th>Started</th><th>Last Seen</th><th>Actions</th>
            </tr>
          </thead>
          <tbody>
            {sessions.map(s => (
              <tr key={s.id}>
                <td style={{ fontFamily: 'monospace' }}>{s.id.slice(0, 8)}</td>
                <td>{s.display_name || '—'}</td>
                <td>{s.agent_type}</td>
                <td style={{ fontFamily: 'monospace' }}>{s.branch_name || '—'}</td>
                <td>{s.ticket_id || '—'}</td>
                <td><span className={`badge ${statusBadge(s.status)}`}>{s.status}</span></td>
                <td>{timeAgo(s.started_at)}</td>
                <td>{timeAgo(s.last_seen_at)}</td>
                <td>
                  {!s.ended_at && (
                    <button className="small danger" onClick={() => handleEnd(s.id)}>End</button>
                  )}
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      ) : (
        <div className="empty">No sessions</div>
      )}
    </div>
  );
}
