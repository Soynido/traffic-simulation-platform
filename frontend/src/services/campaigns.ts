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

export async function createCampaign(data: Omit<Campaign, 'id'>) {
  const res = await api.post('/campaigns', data);
  return res.data as Campaign;
}

export async function updateCampaign(id: string, data: Partial<Campaign>) {
  const res = await api.put(`/campaigns/${id}`, data);
  return res.data as Campaign;
}

export async function deleteCampaign(id: string) {
  const res = await api.delete(`/campaigns/${id}`);
  return res.data;
}

export async function startCampaign(id: string) {
  const res = await api.post(`/campaigns/${id}/start`);
  return res.data as Campaign;
}

export async function pauseCampaign(id: string) {
  const res = await api.post(`/campaigns/${id}/pause`);
  return res.data as Campaign;
}

export async function resumeCampaign(id: string) {
  const res = await api.post(`/campaigns/${id}/resume`);
  return res.data as Campaign;
}

export async function stopCampaign(id: string) {
  const res = await api.post(`/campaigns/${id}/stop`);
  return res.data as Campaign;
}

