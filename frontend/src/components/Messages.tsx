import { useState, useCallback } from 'react';
import { api } from '../api';
import { usePolling } from '../hooks';
import type { Message } from '../types';

export default function Messages() {
  const [channel, setChannel] = useState('');
  const [newMsg, setNewMsg] = useState('');
  const [author, setAuthor] = useState('human');

  const fetcher = useCallback(
    () => channel ? api.listChannelMessages(channel) : api.listMessages(),
    [channel]
  );
  const { data: messages, refresh } = usePolling<Message[]>(fetcher, 5000);

  const handlePost = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!newMsg.trim()) return;
    try {
      await api.postMessage({
        channel: channel || 'common',
        author_type: 'human',
        author_name: author,
        message: newMsg,
      });
      setNewMsg('');
      refresh();
    } catch (err: any) {
      alert(err.message);
    }
  };

  const channels = ['common', 'resource/shared-dev'];
  const uniqueChannels = messages
    ? [...new Set(messages.map(m => m.channel))]
        .filter(c => !channels.includes(c))
    : [];

  return (
    <div>
      <h2>Messages</h2>

      <div className="toolbar">
        <select
          value={channel}
          onChange={(e) => setChannel(e.target.value)}
          style={{ background: 'var(--bg)', border: '1px solid var(--border)', color: 'var(--text)', padding: '8px', borderRadius: 6 }}
        >
          <option value="">All channels</option>
          {[...channels, ...uniqueChannels].map(c => (
            <option key={c} value={c}>#{c}</option>
          ))}
        </select>
      </div>

      <div className="msg-feed">
        {messages && messages.length > 0 ? (
          [...messages].reverse().map(m => (
            <div key={m.id} className="msg-item">
              <div className="msg-meta">
                {new Date(m.created_at).toLocaleTimeString()} · #{m.channel} · [{m.author_type}] {m.author_name}
              </div>
              <div>{m.message}</div>
            </div>
          ))
        ) : (
          <div className="empty">No messages yet</div>
        )}
      </div>

      <form className="msg-form" onSubmit={handlePost}>
        <input
          value={author}
          onChange={(e) => setAuthor(e.target.value)}
          placeholder="Author"
          style={{ maxWidth: 120 }}
        />
        <input
          value={newMsg}
          onChange={(e) => setNewMsg(e.target.value)}
          placeholder="Type a message..."
        />
        <button type="submit">Send</button>
      </form>
    </div>
  );
}
