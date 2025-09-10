'use client';

import { useState, useEffect } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Button } from '@/components/ui/button';
import { 
  CheckCircle, 
  AlertCircle, 
  Globe, 
  Clock, 
  Activity,
  Eye,
  RefreshCw,
  ExternalLink
} from 'lucide-react';

interface VisitData {
  id: string;
  session_id: string;
  url: string;
  title: string;
  visit_order: number;
  arrived_at: string;
  left_at: string | null;
  dwell_time_ms: number | null;
  actions_count: number;
  scroll_depth_percent: number;
  status: 'success' | 'failed' | 'timeout';
  http_status?: number;
  load_time_ms?: number;
}

interface VisitVerificationProps {
  campaignId: string;
  campaignName: string;
}

export function VisitVerificationDashboard({ campaignId, campaignName }: VisitVerificationProps) {
  const [visits, setVisits] = useState<VisitData[]>([]);
  const [loading, setLoading] = useState(true);
  const [stats, setStats] = useState({
    totalVisits: 0,
    successfulVisits: 0,
    failedVisits: 0,
    avgLoadTime: 0,
    avgDwellTime: 0,
    totalActions: 0
  });

  const fetchVisitData = async () => {
    try {
      setLoading(true);
      // API call pour récupérer les visites de la campagne
      const response = await fetch(`/api/campaigns/${campaignId}/visits`);
      const data = await response.json();
      
      const visitList = Array.isArray(data) ? data : data.visits || [];
      setVisits(visitList);
      
      // Calculer les statistiques
      const total = visitList.length;
      const successful = visitList.filter(v => v.status === 'success').length;
      const failed = visitList.filter(v => v.status === 'failed').length;
      const avgLoad = visitList.reduce((sum, v) => sum + (v.load_time_ms || 0), 0) / total || 0;
      const avgDwell = visitList.reduce((sum, v) => sum + (v.dwell_time_ms || 0), 0) / total || 0;
      const totalActs = visitList.reduce((sum, v) => sum + v.actions_count, 0);
      
      setStats({
        totalVisits: total,
        successfulVisits: successful,
        failedVisits: failed,
        avgLoadTime: Math.round(avgLoad),
        avgDwellTime: Math.round(avgDwell),
        totalActions: totalActs
      });
    } catch (error) {
      console.error('Erreur lors du chargement des visites:', error);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchVisitData();
    // Actualisation automatique toutes les 30 secondes
    const interval = setInterval(fetchVisitData, 30000);
    return () => clearInterval(interval);
  }, [campaignId]);

  const formatDuration = (ms: number | null) => {
    if (!ms) return 'N/A';
    if (ms < 1000) return `${ms}ms`;
    const seconds = Math.round(ms / 1000);
    return `${seconds}s`;
  };

  const formatTime = (dateString: string) => {
    return new Date(dateString).toLocaleTimeString();
  };

  const getStatusIcon = (status: string) => {
    switch (status) {
      case 'success':
        return <CheckCircle className="h-4 w-4 text-green-500" />;
      case 'failed':
        return <AlertCircle className="h-4 w-4 text-red-500" />;
      default:
        return <Clock className="h-4 w-4 text-yellow-500" />;
    }
  };

  const getStatusBadge = (status: string) => {
    const variants = {
      success: 'bg-green-100 text-green-800',
      failed: 'bg-red-100 text-red-800',
      timeout: 'bg-yellow-100 text-yellow-800'
    };
    
    return (
      <Badge className={variants[status as keyof typeof variants] || 'bg-gray-100 text-gray-800'}>
        {status.charAt(0).toUpperCase() + status.slice(1)}
      </Badge>
    );
  };

  return (
    <div className="space-y-6">
      {/* Header avec statistiques */}
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-2xl font-bold">Vérification des Visites</h2>
          <p className="text-muted-foreground">Campagne : {campaignName}</p>
        </div>
        <Button onClick={fetchVisitData} disabled={loading}>
          <RefreshCw className="h-4 w-4 mr-2" />
          Actualiser
        </Button>
      </div>

      {/* Statistiques globales */}
      <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-6 gap-4">
        <Card>
          <CardContent className="p-4">
            <div className="flex items-center space-x-2">
              <Globe className="h-5 w-5 text-blue-500" />
              <div>
                <p className="text-sm text-muted-foreground">Total Visites</p>
                <p className="text-2xl font-bold">{stats.totalVisits}</p>
              </div>
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardContent className="p-4">
            <div className="flex items-center space-x-2">
              <CheckCircle className="h-5 w-5 text-green-500" />
              <div>
                <p className="text-sm text-muted-foreground">Réussies</p>
                <p className="text-2xl font-bold text-green-600">{stats.successfulVisits}</p>
              </div>
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardContent className="p-4">
            <div className="flex items-center space-x-2">
              <AlertCircle className="h-5 w-5 text-red-500" />
              <div>
                <p className="text-sm text-muted-foreground">Échecs</p>
                <p className="text-2xl font-bold text-red-600">{stats.failedVisits}</p>
              </div>
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardContent className="p-4">
            <div className="flex items-center space-x-2">
              <Clock className="h-5 w-5 text-blue-500" />
              <div>
                <p className="text-sm text-muted-foreground">Chargement Moy.</p>
                <p className="text-2xl font-bold">{formatDuration(stats.avgLoadTime)}</p>
              </div>
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardContent className="p-4">
            <div className="flex items-center space-x-2">
              <Eye className="h-5 w-5 text-purple-500" />
              <div>
                <p className="text-sm text-muted-foreground">Temps Moy.</p>
                <p className="text-2xl font-bold">{formatDuration(stats.avgDwellTime)}</p>
              </div>
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardContent className="p-4">
            <div className="flex items-center space-x-2">
              <Activity className="h-5 w-5 text-orange-500" />
              <div>
                <p className="text-sm text-muted-foreground">Total Actions</p>
                <p className="text-2xl font-bold">{stats.totalActions}</p>
              </div>
            </div>
          </CardContent>
        </Card>
      </div>

      {/* Tableau détaillé des visites */}
      <Card>
        <CardHeader>
          <CardTitle>Historique des Visites en Temps Réel</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="space-y-4">
            {loading ? (
              <div className="text-center py-8">
                <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-500 mx-auto"></div>
                <p className="text-muted-foreground mt-2">Chargement des visites...</p>
              </div>
            ) : visits.length === 0 ? (
              <div className="text-center py-8 text-muted-foreground">
                <Globe className="h-12 w-12 mx-auto mb-4 opacity-50" />
                <p>Aucune visite enregistrée pour cette campagne</p>
              </div>
            ) : (
              <div className="space-y-3">
                {visits.slice(0, 20).map((visit) => (
                  <div
                    key={visit.id}
                    className="flex items-center justify-between p-4 border rounded-lg hover:bg-muted/50"
                  >
                    <div className="flex items-center space-x-4 flex-1">
                      {getStatusIcon(visit.status)}
                      <div className="flex-1 min-w-0">
                        <div className="flex items-center space-x-2">
                          <p className="font-medium truncate">{visit.title || 'Page sans titre'}</p>
                          {getStatusBadge(visit.status)}
                        </div>
                        <div className="flex items-center space-x-4 text-sm text-muted-foreground">
                          <span className="truncate max-w-md">{visit.url}</span>
                          <span>#{visit.visit_order}</span>
                          <span>{formatTime(visit.arrived_at)}</span>
                        </div>
                      </div>
                    </div>
                    
                    <div className="flex items-center space-x-6 text-sm">
                      <div className="text-center">
                        <p className="text-xs text-muted-foreground">Temps</p>
                        <p className="font-medium">{formatDuration(visit.dwell_time_ms)}</p>
                      </div>
                      <div className="text-center">
                        <p className="text-xs text-muted-foreground">Actions</p>
                        <p className="font-medium">{visit.actions_count}</p>
                      </div>
                      <div className="text-center">
                        <p className="text-xs text-muted-foreground">Scroll</p>
                        <p className="font-medium">{visit.scroll_depth_percent}%</p>
                      </div>
                      <Button
                        variant="ghost"
                        size="sm"
                        onClick={() => window.open(visit.url, '_blank')}
                      >
                        <ExternalLink className="h-4 w-4" />
                      </Button>
                    </div>
                  </div>
                ))}
              </div>
            )}
          </div>
        </CardContent>
      </Card>
    </div>
  );
}