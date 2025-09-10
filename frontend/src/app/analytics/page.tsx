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

  // Mock data - in real app, this would come from API
  useEffect(() => {
    const fetchData = async () => {
      setLoading(true);
      // Simulate API call
      await new Promise(resolve => setTimeout(resolve, 1000));
      
      setData({
        totalSessions: 2456,
        completedSessions: 2149,
        failedSessions: 307,
        successRate: 87.5,
        avgSessionDuration: 145,
        avgPagesPerSession: 4.2,
        avgActionsPerSession: 12.8,
        avgRhythmScore: 0.73,
        detectionRiskScore: 0.15,
        sessionTimeline: [
          { timestamp: '2024-01-15T00:00:00Z', sessions: 45, completed: 42, failed: 3 },
          { timestamp: '2024-01-15T01:00:00Z', sessions: 52, completed: 48, failed: 4 },
          { timestamp: '2024-01-15T02:00:00Z', sessions: 38, completed: 35, failed: 3 },
          { timestamp: '2024-01-15T03:00:00Z', sessions: 41, completed: 38, failed: 3 },
          { timestamp: '2024-01-15T04:00:00Z', sessions: 29, completed: 27, failed: 2 },
          { timestamp: '2024-01-15T05:00:00Z', sessions: 33, completed: 31, failed: 2 },
          { timestamp: '2024-01-15T06:00:00Z', sessions: 47, completed: 44, failed: 3 },
          { timestamp: '2024-01-15T07:00:00Z', sessions: 58, completed: 54, failed: 4 },
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
          { metric: 'Scroll Depth', human: 68, simulated: 65, difference: 3 },
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
