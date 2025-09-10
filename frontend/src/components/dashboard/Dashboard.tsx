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

  // Mock data - in real app, this would come from API
  useEffect(() => {
    const fetchData = async () => {
      setLoading(true);
      // Simulate API call
      await new Promise(resolve => setTimeout(resolve, 1000));
      
      setData({
        totalPersonas: 12,
        totalCampaigns: 8,
        activeSessions: 156,
        successRate: 87.5,
        sessionTimeline: [
          { timestamp: '2024-01-15T00:00:00Z', sessions: 45, completed: 42, failed: 3 },
          { timestamp: '2024-01-15T01:00:00Z', sessions: 52, completed: 48, failed: 4 },
          { timestamp: '2024-01-15T02:00:00Z', sessions: 38, completed: 35, failed: 3 },
          { timestamp: '2024-01-15T03:00:00Z', sessions: 41, completed: 38, failed: 3 },
          { timestamp: '2024-01-15T04:00:00Z', sessions: 29, completed: 27, failed: 2 },
          { timestamp: '2024-01-15T05:00:00Z', sessions: 33, completed: 31, failed: 2 },
        ],
        personaDistribution: [
          { name: 'Rapid Visitor', value: 45, color: '#3b82f6' },
          { name: 'Careful Reader', value: 32, color: '#10b981' },
          { name: 'Social Browser', value: 23, color: '#f59e0b' },
          { name: 'Mobile User', value: 18, color: '#ef4444' },
        ],
        comparisonData: [
          { metric: 'Page Views', human: 1200, simulated: 1150, difference: 50 },
          { metric: 'Session Duration', human: 180, simulated: 175, difference: 5 },
          { metric: 'Bounce Rate', human: 35, simulated: 38, difference: 3 },
          { metric: 'Click Rate', human: 12, simulated: 11, difference: 1 },
        ],
      });
      setLoading(false);
    };

    fetchData();
  }, []);

  const handleRefresh = async () => {
    setRefreshing(true);
    // Simulate refresh
    await new Promise(resolve => setTimeout(resolve, 500));
    setRefreshing(false);
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
