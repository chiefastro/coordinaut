import { useState } from 'react';
import Dashboard from './components/Dashboard';
import Sessions from './components/Sessions';
import Leases from './components/Leases';
import Queue from './components/Queue';
import Messages from './components/Messages';
import Events from './components/Events';
import Tickets from './components/Tickets';
import Repos from './components/Repos';

type Page = 'dashboard' | 'sessions' | 'leases' | 'queue' | 'messages' | 'events' | 'tickets' | 'repos';

const pages: { key: Page; label: string }[] = [
  { key: 'dashboard', label: 'Dashboard' },
  { key: 'repos', label: 'Repos' },
  { key: 'sessions', label: 'Sessions' },
  { key: 'leases', label: 'Leases' },
  { key: 'queue', label: 'Queue' },
  { key: 'tickets', label: 'Tickets' },
  { key: 'messages', label: 'Messages' },
  { key: 'events', label: 'Events' },
];

export default function App() {
  const [page, setPage] = useState<Page>('dashboard');

  const renderPage = () => {
    switch (page) {
      case 'dashboard': return <Dashboard />;
      case 'repos': return <Repos />;
      case 'sessions': return <Sessions />;
      case 'leases': return <Leases />;
      case 'queue': return <Queue />;
      case 'messages': return <Messages />;
      case 'events': return <Events />;
      case 'tickets': return <Tickets />;
    }
  };

  return (
    <div className="app">
      <div className="sidebar">
        <h1>Coordinaut</h1>
        <nav>
          {pages.map(p => (
            <a
              key={p.key}
              href="#"
              className={page === p.key ? 'active' : ''}
              onClick={(e) => { e.preventDefault(); setPage(p.key); }}
            >
              {p.label}
            </a>
          ))}
        </nav>
      </div>
      <div className="main">
        {renderPage()}
      </div>
    </div>
  );
}
