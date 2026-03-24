import { useCallback } from 'react';
import { api } from '../api';
import { usePolling, timeAgo, countdown } from '../hooks';
import type { Session, Lease, QueueEntry, WorkflowEvent } from '../types';

export default function Dashboard() {
  const { data: sessions } = usePolling<Session[]>(
    useCallback(() => api.listSessions(true), []), 5000
  );
  const { data: leases } = usePolling<Lease[]>(
    useCallback(() => api.getActiveLeases(), []), 5000
  );
  const { data: queue } = usePolling<QueueEntry[]>(
    useCallback(() => api.listQueue(), []), 5000
  );
  const { data: events } = usePolling<WorkflowEvent[]>(
    useCallback(() => api.listEvents(15), []), 5000
  );

  const activeLease = leases?.find(l => l.resource_key === 'shared-dev');

  return (
    <div>
      <h2>Dashboard</h2>
      <div className="cards">
        <div className="card">
          <div className="label">Active Sessions</div>
          <div className="value">{sessions?.length ?? '—'}</div>
        </div>
        <div className="card">
          <div className="label">shared-dev Owner</div>
          <div className="value" style={{ fontSize: 16 }}>
            {activeLease
              ? <><span className="badge active">LEASED</span> {activeLease.session_id.slice(0, 8)}</>
              : <span className="badge idle">AVAILABLE</span>}
          </div>
          {activeLease && (() => {
            const cd = countdown(activeLease.expires_at);
            return <div className={`countdown ${cd.level}`} style={{ marginTop: 4 }}>
              TTL: {cd.text}
            </div>;
          })()}
        </div>
        <div className="card">
          <div className="label">Queue Length</div>
          <div className="value">{queue?.length ?? '—'}</div>
        </div>
      </div>

      {activeLease && (
        <div className="section">
          <h3>Active Lease Details</h3>
          <div className="card">
            <div><strong>Session:</strong> {activeLease.session_id.slice(0, 8)}</div>
            <div><strong>Ticket:</strong> {activeLease.ticket_identifier || '—'}</div>
            <div><strong>Commit:</strong> {activeLease.commit_sha || '—'}</div>
            <div><strong>Acquired:</strong> {timeAgo(activeLease.acquired_at)}</div>
            <div><strong>Last Heartbeat:</strong> {timeAgo(activeLease.heartbeat_at)}</div>
          </div>
        </div>
      )}

      {queue && queue.length > 0 && (
        <div className="section">
          <h3>Waiting in Queue</h3>
          <table>
            <thead>
              <tr><th>#</th><th>Session</th><th>Ticket</th><th>Priority</th><th>Waiting</th></tr>
            </thead>
            <tbody>
              {queue.map((q, i) => (
                <tr key={q.id}>
                  <td>{i + 1}</td>
                  <td>{q.session_id.slice(0, 8)}</td>
                  <td>{q.ticket_identifier || '—'}</td>
                  <td>{q.priority}</td>
                  <td>{timeAgo(q.requested_at)}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}

      <div className="section">
        <h3>Recent Events</h3>
        {events && events.length > 0 ? (
          <div className="event-list">
            {events.map(e => (
              <div key={e.id} className="event-item">
                <span className="event-time">{new Date(e.timestamp).toLocaleTimeString()}</span>
                <span className="event-type">{e.event_type}</span>
                <span>{e.message}</span>
              </div>
            ))}
          </div>
        ) : (
          <div className="empty">No recent events</div>
        )}
      </div>
    </div>
  );
}
