import { api } from '@/services/api';

export type Session = {
  id: string;
  campaign_id: string;
  persona_id: string;
  status: string;
  start_url: string;
  user_agent: string;
  viewport_width: number;
  viewport_height: number;
  session_duration_ms?: number | null;
  pages_visited: number;
  total_actions: number;
  error_message?: string | null;
  created_at: string;
  started_at?: string | null;
  completed_at?: string | null;
};

export type Paginated<T> = {
  items: T[];
  page: number;
  limit: number;
  total: number;
  pages: number;
};

export async function listSessions(params?: { page?: number; limit?: number }) {
  const res = await api.get('/sessions', { params });
  return res.data as Paginated<Session> | Session[]; // backend may return paginated or plain list
}

export async function listSessionsByCampaign(campaignId: string, params?: { page?: number; limit?: number }) {
  const res = await api.get(`/sessions/campaign/${campaignId}`, { params });
  return res.data as Paginated<Session> | Session[];
}

export async function getSession(sessionId: string) {
  const res = await api.get(`/sessions/${sessionId}`);
  return res.data as Session;
}

