import { useState, useCallback } from 'react';
import { api } from '../api';
import { usePolling } from '../hooks';
import type { Ticket } from '../types';

export default function Tickets() {
  const { data: tickets, refresh } = usePolling<Ticket[]>(
    useCallback(() => api.listTickets(), []), 10000
  );
  const [importing, setImporting] = useState(false);
  const [launching, setLaunching] = useState<string | null>(null);

  const handleImport = async () => {
    setImporting(true);
    try {
      await api.importLinear();
      refresh();
    } catch (e: any) {
      alert(e.message);
    }
    setImporting(false);
  };

  const handleLaunch = async (identifier: string) => {
    setLaunching(identifier);
    try {
      const result = await api.launchAgent({ ticket_identifier: identifier });
      alert(result.message);
    } catch (e: any) {
      alert(e.message);
    }
    setLaunching(null);
  };

  const parseLabels = (json: string | null): string[] => {
    if (!json) return [];
    try { return JSON.parse(json); } catch { return []; }
  };

  return (
    <div>
      <h2>Tickets</h2>

      <div className="toolbar">
        <button onClick={handleImport} disabled={importing}>
          {importing ? 'Importing...' : 'Import from Linear'}
        </button>
      </div>

      {tickets && tickets.length > 0 ? (
        <table>
          <thead>
            <tr>
              <th>Identifier</th><th>Title</th><th>State</th><th>Assignee</th>
              <th>Labels</th><th>Source</th><th>Actions</th>
            </tr>
          </thead>
          <tbody>
            {tickets.map(t => (
              <tr key={t.id}>
                <td>
                  {t.url ? (
                    <a href={t.url} target="_blank" rel="noopener noreferrer"
                       style={{ color: 'var(--accent)' }}>
                      {t.identifier}
                    </a>
                  ) : t.identifier}
                </td>
                <td>{t.title}</td>
                <td><span className="badge blue">{t.state}</span></td>
                <td>{t.assignee || '—'}</td>
                <td>
                  {parseLabels(t.labels_json).map(l => (
                    <span key={l} className="badge" style={{ marginRight: 4, background: 'var(--bg-hover)' }}>{l}</span>
                  ))}
                </td>
                <td>{t.source}</td>
                <td>
                  <button
                    className="small"
                    onClick={() => handleLaunch(t.identifier)}
                    disabled={launching === t.identifier}
                  >
                    {launching === t.identifier ? '...' : 'Launch Agent'}
                  </button>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      ) : (
        <div className="empty">No tickets — import from Linear or create manually</div>
      )}
    </div>
  );
}
