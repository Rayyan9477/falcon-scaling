import axios from 'axios';
import type { QueryRequest, QueryResponse, FilterOptions, StatsResponse, HistoryEntry, FamilyOfficeResult, QueryAnalysis } from '../types';

// In development: Vite's dev proxy handles /api → backend (relative paths).
// In production (Vercel): VITE_API_URL env var points to the Render backend.
const apiBase = import.meta.env.VITE_API_URL
  ? `${import.meta.env.VITE_API_URL}/api/v1`
  : '/api/v1';

const api = axios.create({
  baseURL: apiBase,
  headers: { 'Content-Type': 'application/json' },
});

export async function queryDataset(request: QueryRequest): Promise<QueryResponse> {
  const { data } = await api.post<QueryResponse>('/query', request);
  return data;
}

/** Stream query results via SSE. Calls onToken/onSources/onDone as events arrive. */
export async function queryDatasetStream(
  request: QueryRequest,
  callbacks: {
    onToken: (token: string) => void;
    onSources: (sources: FamilyOfficeResult[], totalMatches: number) => void;
    onDone: (analysis: QueryAnalysis) => void;
    onError: (error: string) => void;
  },
): Promise<void> {
  const url = `${apiBase}/query/stream`;
  const response = await fetch(url, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(request),
  });

  if (!response.ok || !response.body) {
    callbacks.onError(`Request failed: ${response.statusText}`);
    return;
  }

  const reader = response.body.getReader();
  const decoder = new TextDecoder();
  let buffer = '';

  while (true) {
    const { done, value } = await reader.read();
    if (done) break;

    buffer += decoder.decode(value, { stream: true });
    const lines = buffer.split('\n');
    buffer = lines.pop() || '';

    let currentEvent = '';
    for (const line of lines) {
      if (line.startsWith('event: ')) {
        currentEvent = line.slice(7).trim();
      } else if (line.startsWith('data: ')) {
        const data = line.slice(6);
        if (currentEvent === 'token') {
          callbacks.onToken(data);
        } else if (currentEvent === 'sources') {
          try {
            const parsed = JSON.parse(data);
            callbacks.onSources(parsed.sources || [], parsed.total_matches || 0);
          } catch { /* ignore parse errors */ }
        } else if (currentEvent === 'done') {
          try {
            const parsed = JSON.parse(data);
            callbacks.onDone(parsed.query_analysis);
          } catch { /* ignore */ }
        }
        currentEvent = '';
      }
    }
  }
}

export async function getFilters(): Promise<FilterOptions> {
  const { data } = await api.get<FilterOptions>('/filters');
  return data;
}

export async function getStats(): Promise<StatsResponse> {
  const { data } = await api.get<StatsResponse>('/stats');
  return data;
}

export async function healthCheck(): Promise<{ status: string; records: number }> {
  const { data } = await api.get('/health');
  return data;
}

export async function getHistory(limit = 50): Promise<HistoryEntry[]> {
  const { data } = await api.get<HistoryEntry[]>('/history', { params: { limit } });
  return data;
}

export async function clearHistory(): Promise<{ deleted: number }> {
  const { data } = await api.delete<{ deleted: number }>('/history');
  return data;
}
