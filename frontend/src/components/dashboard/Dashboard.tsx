'use client';

import { useState, useEffect } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs';
import { KPICard } from './KPICard';
import { LiveIndicator } from './LiveIndicator';
import { ProgressBar } from './ProgressBar';
import { SessionChart } from '@/components/analytics/SessionChart';
import { PersonaChart } from '@/components/analytics/PersonaChart';
import { ComparisonChart } from '@/components/analytics/ComparisonChart';
import { 
  Users, 
  Target, 
  Activity, 
  TrendingUp,
  Play,
  Pause,
  RefreshCw
} from 'lucide-react';
import { cn } from '@/lib/utils';
import { listCampaigns } from '@/services/campaigns';
import { listPersonas } from '@/services/api';
import { listSessions } from '@/services/sessions';
import { getAnalyticsSummary } from '@/services/analytics';
import { 
  buildSessionTimeline,
  buildPersonaDistribution,
  buildHumanVsSimulatedComparison,
} from '@/utils/chartUtils';

interface DashboardData {
  totalPersonas: number;
  totalCampaigns: number;
  activeSessions: number;
  successRate: number;
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

interface DashboardProps {
  className?: string;
}

export function Dashboard({ className }: DashboardProps) {
  const [data, setData] = useState<DashboardData | null>(null);
  const [loading, setLoading] = useState(true);
  const [refreshing, setRefreshing] = useState(false);

  // Fetch real data from API
  useEffect(() => {
    const fetchData = async () => {
      setLoading(true);
      try {
        const [campaignsRes, personasRes, sessionsRes, analyticsRes] = await Promise.all([
          listCampaigns({ page: 1, limit: 1000 }),
          listPersonas({ page: 1, limit: 1000 }),
          listSessions({ page: 1, limit: 1000 }),
          getAnalyticsSummary({})
        ]);

        // Handle responses
        const campaigns = Array.isArray(campaignsRes) ? campaignsRes : (campaignsRes?.items || []);
        const personas = Array.isArray(personasRes) ? personasRes : (personasRes?.items || []);
        const sessions = Array.isArray(sessionsRes) ? sessionsRes : (sessionsRes?.items || []);

        // Count active sessions (running status)
        const activeSessions = sessions.filter((s: any) => s.status === 'running').length;

        // Build charts with real data
        const sessionTimeline = buildSessionTimeline(
          sessions.map((s: any) => ({ created_at: s.created_at, status: s.status })),
          { bucket: 'hour' }
        );

        const personasById = personas.reduce((acc: any, p: any) => {
          acc[p.id] = { name: p.name };
          return acc;
        }, {});

        const personaDistribution = buildPersonaDistribution(
          sessions.map((s: any) => ({ persona_id: s.persona_id })),
          personasById
        );

        const comparisonData = buildHumanVsSimulatedComparison(analyticsRes, analyticsRes);

        setData({
          totalPersonas: personas.length,
          totalCampaigns: campaigns.length,
          activeSessions,
          successRate: analyticsRes.success_rate * 100,
          sessionTimeline,
          personaDistribution,
          comparisonData,
        });
      } catch (error) {
        console.error('Failed to fetch dashboard data:', error);
        // Fallback to empty/default data
        setData({
          totalPersonas: 0,
          totalCampaigns: 0,
          activeSessions: 0,
          successRate: 0,
          sessionTimeline: [],
          personaDistribution: [],
          comparisonData: [],
        });
      } finally {
        setLoading(false);
      }
    };

    fetchData();
  }, []);

  const handleRefresh = async () => {
    setRefreshing(true);
    try {
      const [campaignsRes, personasRes, sessionsRes, analyticsRes] = await Promise.all([
        listCampaigns({ page: 1, limit: 1000 }),
        listPersonas({ page: 1, limit: 1000 }),
        listSessions({ page: 1, limit: 1000 }),
        getAnalyticsSummary({})
      ]);

      const campaigns = Array.isArray(campaignsRes) ? campaignsRes : (campaignsRes?.items || []);
      const personas = Array.isArray(personasRes) ? personasRes : (personasRes?.items || []);
      const sessions = Array.isArray(sessionsRes) ? sessionsRes : (sessionsRes?.items || []);

      const activeSessions = sessions.filter((s: any) => s.status === 'running').length;
      const sessionTimeline = buildSessionTimeline(
        sessions.map((s: any) => ({ created_at: s.created_at, status: s.status })),
        { bucket: 'hour' }
      );

      const personasById = personas.reduce((acc: any, p: any) => {
        acc[p.id] = { name: p.name };
        return acc;
      }, {});

      const personaDistribution = buildPersonaDistribution(
        sessions.map((s: any) => ({ persona_id: s.persona_id })),
        personasById
      );

      const comparisonData = buildHumanVsSimulatedComparison(analyticsRes, analyticsRes);

      setData({
        totalPersonas: personas.length,
        totalCampaigns: campaigns.length,
        activeSessions,
        successRate: analyticsRes.success_rate * 100,
        sessionTimeline,
        personaDistribution,
        comparisonData,
      });
    } catch (error) {
      console.error('Failed to refresh dashboard data:', error);
    } finally {
      setRefreshing(false);
    }
  };

  if (loading) {
    return (
      <div className={cn('space-y-6', className)}>
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
    );
  }

  if (!data) return null;

  return (
    <div className={cn('space-y-6', className)}>
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold">Dashboard</h1>
          <p className="text-muted-foreground">
            Monitor your traffic simulation campaigns
          </p>
        </div>
        <div className="flex items-center space-x-4">
          <LiveIndicator isLive={true} />
          <Button
            variant="outline"
            size="sm"
            onClick={handleRefresh}
            disabled={refreshing}
          >
            <RefreshCw className={cn('h-4 w-4 mr-2', refreshing && 'animate-spin')} />
            Refresh
          </Button>
        </div>
      </div>

      {/* KPI Cards */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        <KPICard
          title="Total Personas"
          value={data.totalPersonas}
          icon={<Users className="h-4 w-4" />}
          change={{
            value: 12,
            period: 'vs last month',
            isPercentage: false,
          }}
          status="success"
        />
        <KPICard
          title="Active Campaigns"
          value={data.totalCampaigns}
          icon={<Target className="h-4 w-4" />}
          change={{
            value: 8,
            period: 'vs last month',
            isPercentage: false,
          }}
          status="success"
        />
        <KPICard
          title="Active Sessions"
          value={data.activeSessions}
          icon={<Activity className="h-4 w-4" />}
          change={{
            value: 15,
            period: 'vs last hour',
            isPercentage: false,
          }}
          status="warning"
        />
        <KPICard
          title="Success Rate"
          value={`${data.successRate}%`}
          icon={<TrendingUp className="h-4 w-4" />}
          change={{
            value: 2.5,
            period: 'vs last week',
            isPercentage: true,
          }}
          status="success"
        />
      </div>

      {/* Charts */}
      <Tabs defaultValue="sessions" className="space-y-6">
        <TabsList>
          <TabsTrigger value="sessions">Session Analytics</TabsTrigger>
          <TabsTrigger value="personas">Persona Distribution</TabsTrigger>
          <TabsTrigger value="comparison">Human vs Simulated</TabsTrigger>
        </TabsList>
        
        <TabsContent value="sessions" className="space-y-6">
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            <SessionChart
              data={data.sessionTimeline}
              title="Session Timeline"
              height={300}
            />
            <Card>
              <CardHeader>
                <CardTitle>Session Progress</CardTitle>
              </CardHeader>
              <CardContent className="space-y-4">
                <div>
                  <div className="flex justify-between text-sm mb-2">
                    <span>Completed Sessions</span>
                    <span>87.5%</span>
                  </div>
                  <ProgressBar
                    value={87.5}
                    max={100}
                    variant="success"
                    showPercentage={false}
                  />
                </div>
                <div>
                  <div className="flex justify-between text-sm mb-2">
                    <span>Failed Sessions</span>
                    <span>12.5%</span>
                  </div>
                  <ProgressBar
                    value={12.5}
                    max={100}
                    variant="error"
                    showPercentage={false}
                  />
                </div>
              </CardContent>
            </Card>
          </div>
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

      {/* Quick Actions */}
      <Card>
        <CardHeader>
          <CardTitle>Quick Actions</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="flex flex-wrap gap-4">
            <Button>
              <Play className="h-4 w-4 mr-2" />
              Start New Campaign
            </Button>
            <Button variant="outline">
              <Users className="h-4 w-4 mr-2" />
              Create Persona
            </Button>
            <Button variant="outline">
              <Activity className="h-4 w-4 mr-2" />
              View Analytics
            </Button>
          </div>
        </CardContent>
      </Card>
    </div>
  );
}
