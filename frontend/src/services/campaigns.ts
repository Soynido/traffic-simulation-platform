import { api } from '@/services/api';

export type Campaign = {
  id: string;
  name: string;
  description?: string | null;
  target_url: string;
  total_sessions: number;
  concurrent_sessions: number;
  persona_id: string;
  status?: string;
  created_at?: string;
  updated_at?: string;
};

export type Paginated<T> = {
  items: T[];
  page: number;
  limit: number;
  total: number;
  pages: number;
};

export async function listCampaigns(params?: { page?: number; limit?: number }) {
  const res = await api.get('/campaigns', { params });
  return res.data as Paginated<Campaign> | Campaign[];
}

export async function getCampaign(id: string) {
  const res = await api.get(`/campaigns/${id}`);
  return res.data as Campaign;
}

