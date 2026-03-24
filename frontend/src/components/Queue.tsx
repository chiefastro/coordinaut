import { useCallback } from 'react';
import { api } from '../api';
import { usePolling, timeAgo } from '../hooks';
import type { QueueEntry } from '../types';

export default function Queue() {
  const { data: queue } = usePolling<QueueEntry[]>(
    useCallback(() => api.listQueue(), []), 5000
  );

  return (
    <div>
      <h2>Queue</h2>
      {queue && queue.length > 0 ? (
        <table>
          <thead>
            <tr>
              <th>#</th><th>Resource</th><th>Session</th><th>Ticket</th>
              <th>Priority</th><th>State</th><th>Requested</th>
            </tr>
          </thead>
          <tbody>
            {queue.map((q, i) => (
              <tr key={q.id}>
                <td>{i + 1}</td>
                <td>{q.resource_key}</td>
                <td style={{ fontFamily: 'monospace' }}>{q.session_id.slice(0, 8)}</td>
                <td>{q.ticket_identifier || '—'}</td>
                <td>{q.priority}</td>
                <td><span className={`badge ${q.state}`}>{q.state}</span></td>
                <td>{timeAgo(q.requested_at)}</td>
              </tr>
            ))}
          </tbody>
        </table>
      ) : (
        <div className="empty">Queue is empty — no sessions waiting</div>
      )}
    </div>
  );
}
