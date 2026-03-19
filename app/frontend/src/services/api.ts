import axios from 'axios';
import type { QueryRequest, QueryResponse, FilterOptions, StatsResponse } from '../types';

// In production (Vercel), VITE_API_URL points to the Render backend.
// Locally, Vite's dev proxy handles /api → localhost:9500.
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
