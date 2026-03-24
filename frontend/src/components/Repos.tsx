import { useCallback } from 'react';
import { api } from '../api';
import { usePolling } from '../hooks';

interface RepoInfo {
  path: string;
  name: string;
  current_branch: string;
  remote_url: string;
  branches: { name: string; upstream: string | null; current: boolean }[];
  worktrees: { path: string; head?: string; branch?: string; bare?: boolean }[];
  recent_commits: { sha: string; message: string; author: string; when: string }[];
  changed_files: number;
  error?: string;
}

interface DiscoveredSession {
  pid: string;
  cwd: string | null;
  resume_id: string | null;
  agent_type: string;
}

export default function Repos() {
  const { data: repos } = usePolling<RepoInfo[]>(
    useCallback(() => api.listRepos(), []), 10000
  );
  const { data: discovered } = usePolling<DiscoveredSession[]>(
    useCallback(() => api.discoverSessions(), []), 10000
  );

  return (
    <div>
      <h2>Repositories</h2>

      {repos && repos.length > 0 ? (
        repos.map(repo => (
          <div key={repo.path} style={{ marginBottom: 28 }}>
            <div className="card" style={{ marginBottom: 16 }}>
              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                <div>
                  <span style={{ fontSize: 18, fontWeight: 700 }}>{repo.name}</span>
                  <span style={{ color: 'var(--text-dim)', marginLeft: 12, fontSize: 12 }}>{repo.path}</span>
                </div>
                <div>
                  <span className="badge blue" style={{ marginRight: 8 }}>{repo.current_branch}</span>
                  {repo.changed_files > 0 && (
                    <span className="badge yellow">{repo.changed_files} changed</span>
                  )}
                </div>
              </div>
              <div style={{ color: 'var(--text-dim)', fontSize: 12, marginTop: 4 }}>
                {repo.remote_url}
              </div>
            </div>

            <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 16 }}>
              {/* Worktrees */}
              <div className="section">
                <h3>Worktrees ({repo.worktrees.length})</h3>
                <table>
                  <thead>
                    <tr><th>Path</th><th>Branch</th><th>HEAD</th></tr>
                  </thead>
                  <tbody>
                    {repo.worktrees.map(wt => (
                      <tr key={wt.path}>
                        <td style={{ fontSize: 12 }}>{wt.path.split('/').slice(-2).join('/')}</td>
                        <td><span className="badge blue">{wt.branch || '—'}</span></td>
                        <td style={{ fontFamily: 'monospace', fontSize: 11 }}>{wt.head || '—'}</td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>

              {/* Branches */}
              <div className="section">
                <h3>Branches ({repo.branches.length})</h3>
                <table>
                  <thead>
                    <tr><th>Name</th><th>Upstream</th></tr>
                  </thead>
                  <tbody>
                    {repo.branches.map(b => (
                      <tr key={b.name}>
                        <td>
                          {b.current && <span style={{ color: 'var(--green)', marginRight: 4 }}>*</span>}
                          {b.name}
                        </td>
                        <td style={{ color: 'var(--text-dim)', fontSize: 12 }}>{b.upstream || '—'}</td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </div>

            {/* Recent commits */}
            <div className="section">
              <h3>Recent Commits</h3>
              <div className="event-list">
                {repo.recent_commits.map(c => (
                  <div key={c.sha} className="event-item">
                    <span className="event-time" style={{ minWidth: 70 }}>{c.sha}</span>
                    <span style={{ flex: 1 }}>{c.message}</span>
                    <span style={{ color: 'var(--text-dim)', fontSize: 11, whiteSpace: 'nowrap' }}>
                      {c.author} · {c.when}
                    </span>
                  </div>
                ))}
              </div>
            </div>
          </div>
        ))
      ) : (
        <div className="empty">
          No target repos configured. Set <code>COORDINAUT_TARGET_REPOS</code> in .env
        </div>
      )}

      {/* Discovered Claude Sessions */}
      <div className="section" style={{ marginTop: 32 }}>
        <h3>Discovered Claude Code Processes ({discovered?.length ?? 0})</h3>
        {discovered && discovered.length > 0 ? (
          <table>
            <thead>
              <tr><th>PID</th><th>Working Directory</th><th>Session ID</th></tr>
            </thead>
            <tbody>
              {discovered.map(s => (
                <tr key={s.pid}>
                  <td style={{ fontFamily: 'monospace' }}>{s.pid}</td>
                  <td style={{ fontSize: 12 }}>{s.cwd || '—'}</td>
                  <td style={{ fontFamily: 'monospace', fontSize: 11 }}>{s.resume_id || '—'}</td>
                </tr>
              ))}
            </tbody>
          </table>
        ) : (
          <div className="empty">No Claude Code processes detected</div>
        )}
      </div>
    </div>
  );
}
