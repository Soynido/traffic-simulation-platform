'use client';

import { useState, useEffect, useRef } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { 
  Activity, 
  Globe, 
  User, 
  Clock, 
  CheckCircle, 
  AlertCircle,
  Play,
  Pause,
  Eye,
  MousePointer,
  Scroll,
  ExternalLink
} from 'lucide-react';

interface LogEvent {
  timestamp: string;
  type: 'session' | 'page_visit' | 'action' | 'error';
  action: string;
  details: {
    [key: string]: any;
  };
}

interface LiveActivityLogsProps {
  campaignId: string;
  campaignName: string;
  isRunning: boolean;
}

export function LiveActivityLogs({ campaignId, campaignName, isRunning }: LiveActivityLogsProps) {
  const [logs, setLogs] = useState<LogEvent[]>([]);
  const [isAutoRefresh, setIsAutoRefresh] = useState(true);
  const [loading, setLoading] = useState(false);
  const logsEndRef = useRef<HTMLDivElement>(null);

  const fetchLiveLogs = async () => {
    try {
      setLoading(true);
      const since = new Date(Date.now() - 10 * 60 * 1000).toISOString(); // Last 10 minutes
      const response = await fetch(`/api/campaigns/${campaignId}/live-logs?since=${since}&limit=50`);
      
      if (response.ok) {
        const data = await response.json();
        setLogs(data.events || []);
        
        // Auto-scroll to bottom for new events
        if (isAutoRefresh) {
          setTimeout(() => {
            logsEndRef.current?.scrollIntoView({ behavior: 'smooth' });
          }, 100);
        }
      }
    } catch (error) {
      console.error('Erreur lors du chargement des logs:', error);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchLiveLogs();

    if (isRunning && isAutoRefresh) {
      const interval = setInterval(fetchLiveLogs, 2000); // Update every 2 seconds
      return () => clearInterval(interval);
    }
  }, [campaignId, isRunning, isAutoRefresh]);

  const formatTime = (timestamp: string) => {
    return new Date(timestamp).toLocaleTimeString('fr-FR', {
      hour: '2-digit',
      minute: '2-digit',
      second: '2-digit'
    });
  };

  const getEventIcon = (event: LogEvent) => {
    switch (event.type) {
      case 'session':
        if (event.action.includes('running')) return <Play className="h-4 w-4 text-green-500" />;
        if (event.action.includes('completed')) return <CheckCircle className="h-4 w-4 text-blue-500" />;
        if (event.action.includes('failed')) return <AlertCircle className="h-4 w-4 text-red-500" />;
        return <User className="h-4 w-4 text-gray-500" />;
      case 'page_visit':
        return <Globe className="h-4 w-4 text-blue-500" />;
      case 'action':
        return <MousePointer className="h-4 w-4 text-purple-500" />;
      default:
        return <Activity className="h-4 w-4 text-gray-500" />;
    }
  };

  const getEventBadge = (event: LogEvent) => {
    switch (event.type) {
      case 'session':
        const status = event.details.status;
        const colors = {
          running: 'bg-green-100 text-green-800',
          completed: 'bg-blue-100 text-blue-800',
          failed: 'bg-red-100 text-red-800',
          paused: 'bg-yellow-100 text-yellow-800'
        };
        return (
          <Badge className={colors[status as keyof typeof colors] || 'bg-gray-100 text-gray-800'}>
            {status}
          </Badge>
        );
      case 'page_visit':
        return (
          <Badge className={event.details.success ? 'bg-green-100 text-green-800' : 'bg-yellow-100 text-yellow-800'}>
            {event.details.success ? 'Réussie' : 'En cours'}
          </Badge>
        );
      default:
        return null;
    }
  };

  const renderEventDetails = (event: LogEvent) => {
    switch (event.type) {
      case 'session':
        return (
          <div className="text-sm text-muted-foreground">
            <div className="flex items-center gap-4">
              <span>Session {event.details.session_id}</span>
              <span>{event.details.pages_visited} pages visitées</span>
              <span>Agent: {event.details.user_agent_type}</span>
            </div>
          </div>
        );
      
      case 'page_visit':
        return (
          <div className="space-y-2">
            <div className="flex items-center gap-2">
              <Globe className="h-3 w-3" />
              <span className="font-mono text-sm">{event.details.url}</span>
              <Button
                variant="ghost"
                size="sm"
                className="h-6 w-6 p-0"
                onClick={() => window.open(event.details.url.replace('...', ''), '_blank')}
              >
                <ExternalLink className="h-3 w-3" />
              </Button>
            </div>
            
            {event.details.title && (
              <div className="text-sm text-muted-foreground">
                📄 {event.details.title}
              </div>
            )}
            
            <div className="flex items-center gap-4 text-xs text-muted-foreground">
              <div className="flex items-center gap-1">
                <Clock className="h-3 w-3" />
                {event.details.dwell_time_ms ? `${Math.round(event.details.dwell_time_ms / 1000)}s` : 'En cours'}
              </div>
              <div className="flex items-center gap-1">
                <MousePointer className="h-3 w-3" />
                {event.details.actions_count} actions
              </div>
              <div className="flex items-center gap-1">
                <Scroll className="h-3 w-3" />
                {event.details.scroll_depth}% défilement
              </div>
              <span>Page #{event.details.visit_order}</span>
            </div>
          </div>
        );
      
      default:
        return (
          <div className="text-sm text-muted-foreground">
            {JSON.stringify(event.details, null, 2)}
          </div>
        );
    }
  };

  return (
    <Card className="h-[500px] flex flex-col">
      <CardHeader className="pb-3">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-2">
            <Activity className="h-5 w-5" />
            <CardTitle className="text-lg">Activité en Temps Réel</CardTitle>
            {isRunning && (
              <div className="flex items-center gap-1">
                <div className="w-2 h-2 bg-green-500 rounded-full animate-pulse"></div>
                <span className="text-xs text-green-600 font-medium">LIVE</span>
              </div>
            )}
          </div>
          
          <div className="flex items-center gap-2">
            <Badge variant="outline" className="text-xs">
              {logs.length} événements
            </Badge>
            <Button
              variant="outline"
              size="sm"
              onClick={() => setIsAutoRefresh(!isAutoRefresh)}
              className={isAutoRefresh ? 'bg-green-50 border-green-200' : ''}
            >
              {isAutoRefresh ? <Pause className="h-4 w-4" /> : <Play className="h-4 w-4" />}
              {isAutoRefresh ? 'Pause' : 'Play'}
            </Button>
          </div>
        </div>
        <p className="text-sm text-muted-foreground">
          Suivi transparent de toutes les visites • Campagne: {campaignName}
        </p>
      </CardHeader>
      
      <CardContent className="flex-1 overflow-hidden">
        <div className="h-full overflow-y-auto space-y-3 pr-2">
          {loading && logs.length === 0 ? (
            <div className="flex items-center justify-center h-32">
              <div className="animate-spin rounded-full h-6 w-6 border-b-2 border-blue-500"></div>
              <span className="ml-2 text-sm text-muted-foreground">Chargement des logs...</span>
            </div>
          ) : logs.length === 0 ? (
            <div className="flex flex-col items-center justify-center h-32 text-muted-foreground">
              <Activity className="h-8 w-8 mb-2 opacity-50" />
              <p className="text-sm">Aucune activité récente</p>
              <p className="text-xs">Les événements apparaîtront ici en temps réel</p>
            </div>
          ) : (
            <>
              {logs.map((event, index) => (
                <div
                  key={`${event.timestamp}-${index}`}
                  className="flex items-start gap-3 p-3 rounded-lg border bg-card hover:bg-muted/50 transition-colors"
                >
                  <div className="flex-shrink-0 mt-0.5">
                    {getEventIcon(event)}
                  </div>
                  
                  <div className="flex-1 min-w-0">
                    <div className="flex items-center gap-2 mb-1">
                      <span className="font-medium text-sm">{event.action}</span>
                      {getEventBadge(event)}
                      <span className="text-xs text-muted-foreground ml-auto">
                        {formatTime(event.timestamp)}
                      </span>
                    </div>
                    
                    {renderEventDetails(event)}
                  </div>
                </div>
              ))}
              <div ref={logsEndRef} />
            </>
          )}
        </div>
      </CardContent>
    </Card>
  );
}