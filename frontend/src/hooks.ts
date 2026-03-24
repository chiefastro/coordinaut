import { useState, useEffect, useCallback } from 'react';

export function usePolling<T>(fetcher: () => Promise<T>, intervalMs = 5000) {
  const [data, setData] = useState<T | null>(null);
  const [error, setError] = useState<string | null>(null);

  const refresh = useCallback(() => {
    fetcher()
      .then(setData)
      .catch((e) => setError(e.message));
  }, [fetcher]);

  useEffect(() => {
    refresh();
    const id = setInterval(refresh, intervalMs);
    return () => clearInterval(id);
  }, [refresh, intervalMs]);

  return { data, error, refresh };
}

export function timeAgo(dateStr: string): string {
  const diff = Date.now() - new Date(dateStr).getTime();
  const secs = Math.floor(diff / 1000);
  if (secs < 60) return `${secs}s ago`;
  const mins = Math.floor(secs / 60);
  if (mins < 60) return `${mins}m ago`;
  const hrs = Math.floor(mins / 60);
  if (hrs < 24) return `${hrs}h ago`;
  return `${Math.floor(hrs / 24)}d ago`;
}

export function countdown(expiresAt: string): { text: string; level: string } {
  const diff = new Date(expiresAt).getTime() - Date.now();
  if (diff <= 0) return { text: 'EXPIRED', level: 'critical' };
  const secs = Math.floor(diff / 1000);
  const mins = Math.floor(secs / 60);
  const remSecs = secs % 60;
  const text = `${mins}:${remSecs.toString().padStart(2, '0')}`;
  if (secs < 60) return { text, level: 'critical' };
  if (secs < 180) return { text, level: 'warning' };
  return { text, level: '' };
}
