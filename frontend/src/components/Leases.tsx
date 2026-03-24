import { useCallback } from 'react';
import { api } from '../api';
import { usePolling, timeAgo, countdown } from '../hooks';
import type { Lease } from '../types';

export default function Leases() {
  const { data: active, refresh } = usePolling<Lease[]>(
    useCallback(() => api.getActiveLeases(), []), 3000
  );
  const { data: history } = usePolling<Lease[]>(
    useCallback(() => api.getLeaseHistory(20), []), 10000
  );

  const handleRelease = async (lease: Lease) => {
    try {
      await api.releaseLease({
        resource_key: lease.resource_key,
        session_id: lease.session_id,
        release_reason: 'Manual release from UI',
      });
      refresh();
    } catch (e: any) {
      alert(e.message);
    }
  };

  return (
    <div>
      <h2>Leases</h2>

      <div className="section">
        <h3>Active Leases</h3>
        {active && active.length > 0 ? (
          <table>
            <thead>
              <tr>
                <th>Resource</th><th>Session</th><th>Ticket</th><th>Commit</th>
                <th>TTL</th><th>Heartbeat</th><th>Actions</th>
              </tr>
            </thead>
            <tbody>
              {active.map(l => {
                const cd = countdown(l.expires_at);
                return (
                  <tr key={l.id}>
                    <td>{l.resource_key}</td>
                    <td style={{ fontFamily: 'monospace' }}>{l.session_id.slice(0, 8)}</td>
                    <td>{l.ticket_identifier || '—'}</td>
                    <td style={{ fontFamily: 'monospace' }}>{l.commit_sha?.slice(0, 7) || '—'}</td>
                    <td><span className={`countdown ${cd.level}`}>{cd.text}</span></td>
                    <td>{timeAgo(l.heartbeat_at)}</td>
                    <td>
                      <button className="small danger" onClick={() => handleRelease(l)}>Release</button>
                    </td>
                  </tr>
                );
              })}
            </tbody>
          </table>
        ) : (
          <div className="empty">No active leases — resources are available</div>
        )}
      </div>

      <div className="section">
        <h3>Lease History</h3>
        {history && history.length > 0 ? (
          <table>
            <thead>
              <tr>
                <th>Resource</th><th>Session</th><th>Ticket</th><th>State</th>
                <th>Acquired</th><th>Released</th><th>Reason</th>
              </tr>
            </thead>
            <tbody>
              {history.map(l => (
                <tr key={l.id}>
                  <td>{l.resource_key}</td>
                  <td style={{ fontFamily: 'monospace' }}>{l.session_id.slice(0, 8)}</td>
                  <td>{l.ticket_identifier || '—'}</td>
                  <td><span className={`badge ${l.state}`}>{l.state}</span></td>
                  <td>{timeAgo(l.acquired_at)}</td>
                  <td>{l.released_at ? timeAgo(l.released_at) : '—'}</td>
                  <td>{l.release_reason || '—'}</td>
                </tr>
              ))}
            </tbody>
          </table>
        ) : (
          <div className="empty">No lease history</div>
        )}
      </div>
    </div>
  );
}
