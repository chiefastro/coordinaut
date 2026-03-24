import { useCallback } from 'react';
import { api } from '../api';
import { usePolling } from '../hooks';
import type { WorkflowEvent } from '../types';

export default function Events() {
  const { data: events } = usePolling<WorkflowEvent[]>(
    useCallback(() => api.listEvents(50), []), 5000
  );

  return (
    <div>
      <h2>Events</h2>
      {events && events.length > 0 ? (
        <div className="event-list">
          {events.map(e => (
            <div key={e.id} className="event-item">
              <span className="event-time">
                {new Date(e.timestamp).toLocaleString()}
              </span>
              <span className="event-type">{e.event_type}</span>
              <span style={{ flex: 1 }}>{e.message}</span>
              {e.session_id && (
                <span style={{ color: 'var(--text-dim)', fontFamily: 'monospace', fontSize: 11 }}>
                  {e.session_id.slice(0, 8)}
                </span>
              )}
            </div>
          ))}
        </div>
      ) : (
        <div className="empty">No events recorded</div>
      )}
    </div>
  );
}
