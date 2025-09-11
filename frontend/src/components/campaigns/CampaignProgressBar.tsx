'use client';

import { useState, useEffect } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { ProgressBar } from '@/components/dashboard/ProgressBar';
import { Badge } from '@/components/ui/badge';
import { Play, Pause, Square, CheckCircle, AlertCircle } from 'lucide-react';
import { connectWebSocket } from '@/services/websocket';

interface CampaignProgressProps {
  campaignId: string;
  campaignName: string;
  status: 'pending' | 'running' | 'paused' | 'completed' | 'failed';
  totalSessions: number;
  targetUrl: string;
}

interface SessionProgress {
  completed: number;
  running: number;
  failed: number;
  total: number;
  percentage: number;
}

export function CampaignProgressBar({ 
  campaignId, 
  campaignName, 
  status, 
  totalSessions,
  targetUrl 
}: CampaignProgressProps) {
  const [progress, setProgress] = useState<SessionProgress>({
    completed: 0,
    running: 0,
    failed: 0,
    total: totalSessions,
    percentage: 0
  });
  const [isLive, setIsLive] = useState(false);

  // Fetch real-time metrics from API
  useEffect(() => {
    const fetchRealMetrics = async () => {
      try {
        const response = await fetch(`/api/campaigns/${campaignId}/real-time-metrics`);
        if (response.ok) {
          const data = await response.json();
          setProgress({
            completed: data.sessions.completed,
            running: data.sessions.running,
            failed: data.sessions.failed,
            total: data.sessions.total,
            percentage: data.sessions.progress_percentage
          });
        }
      } catch (error) {
        console.error('Erreur lors de la récupération des métriques:', error);
      }
    };

    // Fetch initial data
    fetchRealMetrics();

    // Update every 3 seconds for running campaigns
    if (status === 'running') {
      const interval = setInterval(fetchRealMetrics, 3000);
      return () => clearInterval(interval);
    }
  }, [campaignId, status]);


  // WebSocket connection for real-time updates (when backend implements it)
  useEffect(() => {
    // Only try WebSocket for running campaigns
    if (status !== 'running') {
      setIsLive(false);
      return;
    }

    const ws = connectWebSocket(`/ws/campaign-progress/${campaignId}`, {
      reconnect: false, // Disable auto-reconnect for now since backend doesn't implement this endpoint
      onOpen: () => setIsLive(true),
      onClose: () => setIsLive(false),
      onError: () => {
        setIsLive(false);
        console.debug('WebSocket connection failed - progress updates will use mock data');
      },
      onMessage: (data) => {
        if (data.type === 'progress_update') {
          setProgress(data.progress);
        }
      },
    });

    return () => ws.close();
  }, [campaignId, status]);

  const getStatusIcon = () => {
    switch (status) {
      case 'running':
        return <Play className="h-4 w-4 text-green-500" />;
      case 'paused':
        return <Pause className="h-4 w-4 text-yellow-500" />;
      case 'completed':
        return <CheckCircle className="h-4 w-4 text-green-500" />;
      case 'failed':
        return <AlertCircle className="h-4 w-4 text-red-500" />;
      default:
        return <Square className="h-4 w-4 text-gray-500" />;
    }
  };

  const getStatusColor = () => {
    switch (status) {
      case 'running':
        return 'bg-green-500';
      case 'paused':
        return 'bg-yellow-500';
      case 'completed':
        return 'bg-blue-500';
      case 'failed':
        return 'bg-red-500';
      default:
        return 'bg-gray-500';
    }
  };

  return (
    <Card className="w-full">
      <CardHeader className="pb-3">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-2">
            {getStatusIcon()}
            <CardTitle className="text-lg">{campaignName}</CardTitle>
            {isLive && status === 'running' && (
              <div className="flex items-center gap-1">
                <div className="w-2 h-2 bg-green-500 rounded-full animate-pulse"></div>
                <span className="text-xs text-green-600">LIVE</span>
              </div>
            )}
          </div>
          <Badge variant={status === 'running' ? 'default' : 'secondary'}>
            {status.charAt(0).toUpperCase() + status.slice(1)}
          </Badge>
        </div>
        <p className="text-sm text-muted-foreground truncate">{targetUrl}</p>
      </CardHeader>
      <CardContent className="space-y-4">
        {/* Main progress */}
        <div>
          <div className="flex justify-between text-sm mb-2">
            <span>Visitors Sent</span>
            <span className="font-mono">
              {progress.completed.toLocaleString()} / {progress.total.toLocaleString()}
              {progress.completed > progress.total && (
                <span className="text-green-600 ml-1">✓ Completed</span>
              )}
            </span>
          </div>
          <ProgressBar
            value={Math.min(progress.completed, progress.total)}
            max={progress.total}
            variant={progress.completed >= progress.total ? "success" : "default"}
            showPercentage={true}
            className="h-3"
          />
          {progress.completed > progress.total && (
            <div className="text-xs text-green-600 mt-1">
              Campaign exceeded target by {((progress.completed / progress.total - 1) * 100).toFixed(0)}%
            </div>
          )}
        </div>

        {/* Detailed breakdown */}
        <div className="grid grid-cols-3 gap-4 text-sm">
          <div className="text-center">
            <div className="text-lg font-bold text-green-600">
              {progress.completed.toLocaleString()}
            </div>
            <div className="text-xs text-muted-foreground">Completed</div>
          </div>
          <div className="text-center">
            <div className="text-lg font-bold text-blue-600">
              {progress.running.toLocaleString()}
            </div>
            <div className="text-xs text-muted-foreground">Running</div>
          </div>
          <div className="text-center">
            <div className="text-lg font-bold text-red-600">
              {progress.failed.toLocaleString()}
            </div>
            <div className="text-xs text-muted-foreground">Failed</div>
          </div>
        </div>

        {/* Progress indicator for running campaigns */}
        {status === 'running' && (
          <div className="flex items-center gap-2 text-xs text-muted-foreground">
            <div className="flex gap-1">
              <div className={`w-1 h-4 ${getStatusColor()} rounded-full animate-pulse`}></div>
              <div className={`w-1 h-4 ${getStatusColor()} rounded-full animate-pulse`} style={{animationDelay: '0.5s'}}></div>
              <div className={`w-1 h-4 ${getStatusColor()} rounded-full animate-pulse`} style={{animationDelay: '1s'}}></div>
            </div>
            <span>Sending visitors...</span>
          </div>
        )}
      </CardContent>
    </Card>
  );
}