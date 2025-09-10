'use client';

import { useState, useEffect } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { SessionChart } from '@/components/analytics/SessionChart';
import { PersonaChart } from '@/components/analytics/PersonaChart';
import { ComparisonChart } from '@/components/analytics/ComparisonChart';
import { KPICard } from '@/components/dashboard/KPICard';
import { ProgressBar } from '@/components/dashboard/ProgressBar';
import { 
  TrendingUp, 
  Users, 
  Activity, 
  Target,
  RefreshCw
} from 'lucide-react';
import {
  buildSessionTimeline,
  buildPersonaDistribution,
  buildHumanVsSimulatedComparison,
  type TimelinePoint,
} from '@/utils/chartUtils';
import { getAnalyticsSummary, compareAnalytics } from '@/services/analytics';
import { listSessions, listSessionsByCampaign } from '@/services/sessions';
import { listPersonas, type Persona } from '@/services/api';
import { listCampaigns, type Campaign } from '@/services/campaigns';
import { 
  Select,
  SelectTrigger,
  SelectValue,
  SelectContent,
  SelectItem,
} from '@/components/ui/select';
import { connectWebSocket } from '@/services/websocket';
import { Input } from '@/components/ui/input';
import { LiveIndicator } from '@/components/dashboard/LiveIndicator';

interface AnalyticsData {
  totalSessions: number;
  completedSessions: number;
  failedSessions: number;
  successRate: number;
  avgSessionDuration: number;
  avgPagesPerSession: number;
  avgActionsPerSession: number;
  avgRhythmScore: number;
  detectionRiskScore: number;
  sessionTimeline: Array<{
    timestamp: string;
    sessions: number;
    completed: number;
    failed: number;
  }>;
  personaDistribution: Array<{
    name: string;
    value: number;
    color?: string;
  }>;
  comparisonData: Array<{
    metric: string;
    human: number;
    simulated: number;
    difference?: number;
  }>;
}

export default function AnalyticsPage() {
  const [data, setData] = useState<AnalyticsData | null>(null);
  const [loading, setLoading] = useState(true);
  const [refreshing, setRefreshing] = useState(false);
  const [campaigns, setCampaigns] = useState<Campaign[]>([]);
  const [selectedCampaignId, setSelectedCampaignId] = useState<string>('all');
  const [startDate, setStartDate] = useState<string>('');
  const [endDate, setEndDate] = useState<string>('');
  const [liveConnected, setLiveConnected] = useState<boolean>(false);

  // Fetch real data from API
  const fetchData = async () => {
      setLoading(true);
      try {
        const startIso = startDate ? new Date(startDate + 'T00:00:00Z').toISOString() : undefined;
        const endIso = endDate ? new Date(endDate + 'T23:59:59Z').toISOString() : undefined;
        // Fetch campaigns first (for selector)
        const [campaignsRes] = await Promise.all([
          listCampaigns({ page: 1, limit: 100 }),
        ]);
        const campaignItems = Array.isArray(campaignsRes)
          ? (campaignsRes as Campaign[])
          : ((campaignsRes as any)?.items ?? []);
        setCampaigns(campaignItems);

        // Fetch analytics summary and sessions, filtered by campaign if selected
        const [summary, sessionsRes, personasRes] = await Promise.all([
          getAnalyticsSummary({
            campaign_id: selectedCampaignId === 'all' ? undefined : selectedCampaignId,
            start_date: startIso,
            end_date: endIso,
          }),
          selectedCampaignId === 'all'
            ? listSessions({ page: 1, limit: 1000 })
            : listSessionsByCampaign(selectedCampaignId, { page: 1, limit: 1000 }),
          listPersonas({ page: 1, limit: 1000 }),
        ]);

        let sessionItems = Array.isArray(sessionsRes)
          ? sessionsRes
          : (sessionsRes.items ?? []);

        // Client-side filter by date range for sessions (API does not accept dates)
        if (startDate || endDate) {
          const startMs = startDate ? new Date(startDate).getTime() : -Infinity;
          const endMs = endDate ? new Date(endDate).getTime() : Infinity;
          sessionItems = (sessionItems as any[]).filter((s) => {
            const t = new Date(s.created_at).getTime();
            return t >= startMs && t <= endMs;
          });
        }

        // Build charts
        const sessionTimeline: TimelinePoint[] = buildSessionTimeline(
          sessionItems.map((s: any) => ({ created_at: s.created_at, status: s.status })),
          { bucket: 'hour' }
        );

        // For persona distribution, we need names; fallback to IDs if not available here
        let personaItems: Persona[] = [] as any;
        if (Array.isArray(personasRes)) {
          personaItems = personasRes as Persona[];
        } else if (personasRes && Array.isArray((personasRes as any).items)) {
          personaItems = (personasRes as any).items as Persona[];
        }

        const personasById: Record<string, { name: string }> = personaItems.reduce((acc, p) => {
          acc[p.id] = { name: p.name };
          return acc;
        }, {} as Record<string, { name: string }>);
        const personaDistribution = buildPersonaDistribution(
          sessionItems.map((s: any) => ({ persona_id: s.persona_id })),
          personasById
        );

        // Optionally compare two identical criteria to populate comparison chart
        let comparisonData = [] as Array<{ metric: string; human: number; simulated: number; difference: number }>;
        try {
          const cmp = await compareAnalytics([
            { name: 'Human' },
            { name: 'Simulated' },
          ]);
          const human = cmp.results[0]?.summary ?? summary;
          const simulated = cmp.results[1]?.summary ?? summary;
          comparisonData = buildHumanVsSimulatedComparison(human, simulated);
        } catch {
          // Fallback to using the same summary for both
          comparisonData = buildHumanVsSimulatedComparison(summary, summary);
        }

        setData({
          totalSessions: summary.total_sessions,
          completedSessions: summary.completed_sessions,
          failedSessions: summary.failed_sessions,
          successRate: Number((summary.success_rate * 100).toFixed(1)),
          avgSessionDuration: Math.round((summary.avg_session_duration_ms ?? 0) / 1000),
          avgPagesPerSession: Number((summary.avg_pages_per_session ?? 0).toFixed(1)),
          avgActionsPerSession: Number((summary.avg_actions_per_session ?? 0).toFixed(1)),
          avgRhythmScore: Number((summary.avg_rhythm_score ?? 0).toFixed(2)),
          detectionRiskScore: Number((summary.detection_risk_score ?? 0).toFixed(2)),
          sessionTimeline,
          personaDistribution,
          comparisonData,
        });
      } catch (e) {
        // Soft-fail: keep page skeleton visible
        console.error('Failed to load analytics', e);
        setData({
          totalSessions: 0,
          completedSessions: 0,
          failedSessions: 0,
          successRate: 0,
          avgSessionDuration: 0,
          avgPagesPerSession: 0,
          avgActionsPerSession: 0,
          avgRhythmScore: 0,
          detectionRiskScore: 0,
          sessionTimeline: [],
          personaDistribution: [],
          comparisonData: [],
        });
      } finally {
        setLoading(false);
      }
    };

  useEffect(() => {
    fetchData();
  }, [selectedCampaignId, startDate, endDate]);

  // Live updates via WebSocket
  useEffect(() => {
    const params = new URLSearchParams();
    const startIso = startDate ? new Date(startDate + 'T00:00:00Z').toISOString() : undefined;
    const endIso = endDate ? new Date(endDate + 'T23:59:59Z').toISOString() : undefined;
    if (selectedCampaignId && selectedCampaignId !== 'all') params.set('campaign_id', selectedCampaignId);
    if (startIso) params.set('start_date', startIso);
    if (endIso) params.set('end_date', endIso);
    const path = `/ws/campaign-updates${params.toString() ? `?${params.toString()}` : ''}`;

    const ws = connectWebSocket(path, {
      reconnect: true,
      onOpen: () => setLiveConnected(true),
      onClose: () => setLiveConnected(false),
      onError: () => setLiveConnected(false),
      onMessage: () => {
        // Throttle by relying on server tick interval (5s)
        fetchData();
      },
    });

    return () => ws.close();
  }, [selectedCampaignId, startDate, endDate]);

  const handleRefresh = async () => {
    setRefreshing(true);
    // Simulate refresh
    await new Promise(resolve => setTimeout(resolve, 500));
    setRefreshing(false);
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-background p-6">
        <div className="max-w-7xl mx-auto space-y-6">
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
            {[...Array(4)].map((_, i) => (
              <div key={i} className="h-32 bg-muted animate-pulse rounded-lg" />
            ))}
          </div>
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            <div className="h-96 bg-muted animate-pulse rounded-lg" />
            <div className="h-96 bg-muted animate-pulse rounded-lg" />
          </div>
        </div>
      </div>
    );
  }

  if (!data) return null;

  return (
    <div className="min-h-screen bg-background p-6">
      <div className="max-w-7xl mx-auto space-y-6">
        {/* Header */}
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-3xl font-bold">Analytics</h1>
            <p className="text-muted-foreground">
              Detailed insights into your traffic simulation performance
            </p>
          </div>
          <div className="flex items-center gap-3">
            <LiveIndicator isLive={liveConnected} />
            <div className="w-64">
              <Select value={selectedCampaignId} onValueChange={setSelectedCampaignId}>
                <SelectTrigger>
                  <SelectValue placeholder="All campaigns" />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="all">All campaigns</SelectItem>
                  {campaigns.map((c) => (
                    <SelectItem key={c.id} value={c.id}>{c.name}</SelectItem>
                  ))}
                </SelectContent>
              </Select>
            </div>
            <div className="flex items-center gap-2">
              <Input type="date" value={startDate} onChange={(e) => setStartDate(e.target.value)} />
              <span className="text-sm text-muted-foreground">to</span>
              <Input type="date" value={endDate} onChange={(e) => setEndDate(e.target.value)} />
            </div>
            <Button
              variant="outline"
              size="sm"
              onClick={handleRefresh}
              disabled={refreshing}
            >
              <RefreshCw className={`h-4 w-4 mr-2 ${refreshing ? 'animate-spin' : ''}`} />
              Refresh
            </Button>
          </div>
        </div>

        {/* KPI Cards */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
          <KPICard
            title="Total Sessions"
            value={data.totalSessions.toLocaleString()}
            icon={<Activity className="h-4 w-4" />}
            change={{
              value: 12.5,
              period: 'vs last week',
              isPercentage: true,
            }}
            status="success"
          />
          <KPICard
            title="Success Rate"
            value={`${data.successRate}%`}
            icon={<TrendingUp className="h-4 w-4" />}
            change={{
              value: 2.3,
              period: 'vs last week',
              isPercentage: true,
            }}
            status="success"
          />
          <KPICard
            title="Avg Duration"
            value={`${data.avgSessionDuration}s`}
            icon={<Target className="h-4 w-4" />}
            change={{
              value: -5.2,
              period: 'vs last week',
              isPercentage: true,
            }}
            status="warning"
          />
          <KPICard
            title="Detection Risk"
            value={`${(data.detectionRiskScore * 100).toFixed(1)}%`}
            icon={<Users className="h-4 w-4" />}
            change={{
              value: -0.8,
              period: 'vs last week',
              isPercentage: true,
            }}
            status="success"
          />
        </div>

        {/* Detailed Metrics */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
          <Card>
            <CardHeader>
              <CardTitle className="text-lg">Session Quality</CardTitle>
            </CardHeader>
            <CardContent className="space-y-4">
              <div>
                <div className="flex justify-between text-sm mb-2">
                  <span>Rhythm Score</span>
                  <span>{(data.avgRhythmScore * 100).toFixed(1)}%</span>
                </div>
                <ProgressBar
                  value={data.avgRhythmScore * 100}
                  max={100}
                  variant="success"
                  showPercentage={false}
                />
                <p className="text-xs text-muted-foreground mt-1">
                  Higher is more human-like
                </p>
              </div>
              <div>
                <div className="flex justify-between text-sm mb-2">
                  <span>Detection Risk</span>
                  <span>{(data.detectionRiskScore * 100).toFixed(1)}%</span>
                </div>
                <ProgressBar
                  value={data.detectionRiskScore * 100}
                  max={100}
                  variant="error"
                  showPercentage={false}
                />
                <p className="text-xs text-muted-foreground mt-1">
                  Lower is better
                </p>
              </div>
            </CardContent>
          </Card>

          <Card>
            <CardHeader>
              <CardTitle className="text-lg">Session Metrics</CardTitle>
            </CardHeader>
            <CardContent className="space-y-4">
              <div className="text-center">
                <div className="text-2xl font-bold">{data.avgPagesPerSession}</div>
                <div className="text-sm text-muted-foreground">Avg Pages per Session</div>
              </div>
              <div className="text-center">
                <div className="text-2xl font-bold">{data.avgActionsPerSession}</div>
                <div className="text-sm text-muted-foreground">Avg Actions per Session</div>
              </div>
            </CardContent>
          </Card>

          <Card>
            <CardHeader>
              <CardTitle className="text-lg">Session Status</CardTitle>
            </CardHeader>
            <CardContent className="space-y-4">
              <div>
                <div className="flex justify-between text-sm mb-2">
                  <span>Completed</span>
                  <span>{data.completedSessions.toLocaleString()}</span>
                </div>
                <ProgressBar
                  value={data.completedSessions}
                  max={data.totalSessions}
                  variant="success"
                  showPercentage={false}
                />
              </div>
              <div>
                <div className="flex justify-between text-sm mb-2">
                  <span>Failed</span>
                  <span>{data.failedSessions.toLocaleString()}</span>
                </div>
                <ProgressBar
                  value={data.failedSessions}
                  max={data.totalSessions}
                  variant="error"
                  showPercentage={false}
                />
              </div>
            </CardContent>
          </Card>
        </div>

        {/* Charts */}
        <Tabs defaultValue="sessions" className="space-y-6">
          <TabsList>
            <TabsTrigger value="sessions">Session Timeline</TabsTrigger>
            <TabsTrigger value="personas">Persona Distribution</TabsTrigger>
            <TabsTrigger value="comparison">Human vs Simulated</TabsTrigger>
          </TabsList>
          
          <TabsContent value="sessions" className="space-y-6">
            <SessionChart
              data={data.sessionTimeline}
              title="Session Activity Over Time"
              height={400}
            />
          </TabsContent>
          
          <TabsContent value="personas" className="space-y-6">
            <PersonaChart
              data={data.personaDistribution}
              title="Persona Usage Distribution"
              height={400}
            />
          </TabsContent>
          
          <TabsContent value="comparison" className="space-y-6">
            <ComparisonChart
              data={data.comparisonData}
              title="Human vs Simulated Traffic Comparison"
              height={400}
            />
          </TabsContent>
        </Tabs>
      </div>
    </div>
  );
}
