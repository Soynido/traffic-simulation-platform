import { api } from '@/services/api';

export type AnalyticsSummaryResponse = {
  total_sessions: number;
  completed_sessions: number;
  failed_sessions: number;
  success_rate: number;
  avg_session_duration_ms: number;
  avg_pages_per_session: number;
  avg_actions_per_session: number;
  avg_rhythm_score: number;
  detection_risk_score: number;
};

export type ComparisonCriteria = {
  name: string;
  start_date?: string;
  end_date?: string;
  campaign_id?: string;
};

export type ComparisonResponse = {
  criteria: ComparisonCriteria[];
  results: Array<{ name: string; criteria: ComparisonCriteria; summary: AnalyticsSummaryResponse }>;
  comparison_metrics: Record<string, { min: number; max: number; avg: number; variance: number }>;
};

export async function getAnalyticsSummary(params?: Partial<ComparisonCriteria>): Promise<AnalyticsSummaryResponse> {
  const res = await api.get('/analytics/summary', { params });
  return res.data;
}

export async function getCampaignAnalytics(campaignId: string) {
  const res = await api.get(`/analytics/campaigns/${campaignId}`);
  return res.data;
}

export async function compareAnalytics(criteria: ComparisonCriteria[]): Promise<ComparisonResponse> {
  const res = await api.post('/analytics/compare', { criteria });
  return res.data;
}

