'use client';

import { useState, useEffect } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Button } from '@/components/ui/button';
import { 
  Shield, 
  CheckCircle, 
  AlertCircle, 
  Activity, 
  Globe, 
  Clock, 
  TrendingUp,
  Eye,
  MousePointer,
  RefreshCw,
  ExternalLink,
  BarChart3
} from 'lucide-react';
import { ProgressBar } from '@/components/dashboard/ProgressBar';

interface DeliverabilityReport {
  campaign_id: string;
  report_timestamp: string;
  deliverability_score: number;
  statistics: {
    total_visits: number;
    successful_visits: number;
    success_rate: number;
    avg_dwell_time_ms: number;
    total_actions: number;
    unique_urls: number;
  };
  verification_samples: Array<{
    visit_id: string;
    url_domain: string;
    confidence_score: number;
    checks_passed: number;
  }>;
  avg_confidence_score: number;
  quality_indicators: {
    total_visits: number;
    successful_visits: number;
    avg_dwell_time_seconds: number;
    total_user_actions: number;
    unique_pages: number;
  };
  recent_failures: number;
  failure_types: string[];
}

interface DeliverabilityDashboardProps {
  campaignId: string;
  campaignName: string;
  campaignStatus: string;
}

export function DeliverabilityDashboard({ 
  campaignId, 
  campaignName, 
  campaignStatus 
}: DeliverabilityDashboardProps) {
  const [report, setReport] = useState<DeliverabilityReport | null>(null);
  const [loading, setLoading] = useState(true);
  const [lastUpdate, setLastUpdate] = useState<Date>(new Date());

  const fetchReport = async () => {
    try {
      setLoading(true);
      const response = await fetch(`/api/campaigns/${campaignId}/verification-report`);
      
      if (response.ok) {
        const data = await response.json();
        setReport(data);
        setLastUpdate(new Date());
      }
    } catch (error) {
      console.error('Erreur lors du chargement du rapport:', error);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchReport();
    
    // Auto-refresh pour les campagnes actives
    if (campaignStatus === 'running') {
      const interval = setInterval(fetchReport, 30000); // Toutes les 30 secondes
      return () => clearInterval(interval);
    }
  }, [campaignId, campaignStatus]);

  const getScoreColor = (score: number) => {
    if (score >= 90) return 'text-green-600';
    if (score >= 75) return 'text-yellow-600';
    return 'text-red-600';
  };

  const getScoreBadge = (score: number) => {
    if (score >= 90) return 'bg-green-100 text-green-800 border-green-200';
    if (score >= 75) return 'bg-yellow-100 text-yellow-800 border-yellow-200';
    return 'bg-red-100 text-red-800 border-red-200';
  };

  const formatDuration = (ms: number) => {
    if (ms < 1000) return `${ms}ms`;
    const seconds = Math.round(ms / 1000);
    return `${seconds}s`;
  };

  if (loading) {
    return (
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Shield className="h-5 w-5" />
            Garantie de Délivrabilité
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className="flex items-center justify-center h-32">
            <div className="animate-spin rounded-full h-6 w-6 border-b-2 border-blue-500"></div>
            <span className="ml-2 text-sm text-muted-foreground">Analyse en cours...</span>
          </div>
        </CardContent>
      </Card>
    );
  }

  if (!report) {
    return (
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Shield className="h-5 w-5" />
            Garantie de Délivrabilité
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className="text-center py-8 text-muted-foreground">
            <AlertCircle className="h-12 w-12 mx-auto mb-4 opacity-50" />
            <p>Impossible de charger le rapport de délivrabilité</p>
            <Button variant="outline" className="mt-4" onClick={fetchReport}>
              <RefreshCw className="h-4 w-4 mr-2" />
              Réessayer
            </Button>
          </div>
        </CardContent>
      </Card>
    );
  }

  return (
    <div className="space-y-6">
      {/* Score principal de délivrabilité */}
      <Card className="border-2 border-blue-200 bg-blue-50/50">
        <CardHeader>
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-2">
              <Shield className="h-6 w-6 text-blue-600" />
              <CardTitle className="text-xl">Garantie de Délivrabilité à 100%</CardTitle>
            </div>
            <div className="flex items-center gap-2">
              <Badge className={`border ${getScoreBadge(report.deliverability_score)}`}>
                <CheckCircle className="h-3 w-3 mr-1" />
                {report.deliverability_score}% Vérifié
              </Badge>
              <Button variant="outline" size="sm" onClick={fetchReport}>
                <RefreshCw className="h-4 w-4" />
              </Button>
            </div>
          </div>
          <p className="text-sm text-muted-foreground">
            Campagne: {campaignName} • Dernière vérification: {lastUpdate.toLocaleTimeString()}
          </p>
        </CardHeader>
        
        <CardContent className="space-y-6">
          {/* Score principal */}
          <div className="text-center py-6">
            <div className={`text-6xl font-bold ${getScoreColor(report.deliverability_score)}`}>
              {report.deliverability_score}%
            </div>
            <p className="text-lg text-muted-foreground mt-2">
              Taux de Délivrabilité Vérifié
            </p>
            <ProgressBar
              value={report.deliverability_score}
              max={100}
              variant="success"
              className="mt-4 h-3"
              showPercentage={false}
            />
          </div>

          {/* Métriques de qualité */}
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
            <div className="text-center p-4 bg-white rounded-lg border">
              <Globe className="h-8 w-8 mx-auto mb-2 text-blue-500" />
              <div className="text-2xl font-bold">{report.quality_indicators.total_visits}</div>
              <div className="text-sm text-muted-foreground">Visites Totales</div>
            </div>
            
            <div className="text-center p-4 bg-white rounded-lg border">
              <CheckCircle className="h-8 w-8 mx-auto mb-2 text-green-500" />
              <div className="text-2xl font-bold text-green-600">{report.quality_indicators.successful_visits}</div>
              <div className="text-sm text-muted-foreground">Visites Réussies</div>
            </div>
            
            <div className="text-center p-4 bg-white rounded-lg border">
              <Clock className="h-8 w-8 mx-auto mb-2 text-purple-500" />
              <div className="text-2xl font-bold">{report.quality_indicators.avg_dwell_time_seconds}s</div>
              <div className="text-sm text-muted-foreground">Temps Moyen</div>
            </div>
            
            <div className="text-center p-4 bg-white rounded-lg border">
              <MousePointer className="h-8 w-8 mx-auto mb-2 text-orange-500" />
              <div className="text-2xl font-bold">{report.quality_indicators.total_user_actions}</div>
              <div className="text-sm text-muted-foreground">Actions Utilisateur</div>
            </div>
          </div>

          {/* Échantillons de vérification */}
          <div>
            <h4 className="font-semibold mb-3 flex items-center gap-2">
              <BarChart3 className="h-4 w-4" />
              Échantillons de Vérification Récents
            </h4>
            <div className="space-y-2">
              {report.verification_samples.map((sample, index) => (
                <div key={index} className="flex items-center justify-between p-3 bg-white rounded border">
                  <div className="flex items-center gap-3">
                    <Globe className="h-4 w-4 text-muted-foreground" />
                    <div>
                      <div className="font-medium text-sm">{sample.url_domain}</div>
                      <div className="text-xs text-muted-foreground">
                        ID: {sample.visit_id} • {sample.checks_passed}/5 vérifications passées
                      </div>
                    </div>
                  </div>
                  <div className="flex items-center gap-2">
                    <Badge 
                      className={sample.confidence_score >= 0.8 ? 
                        'bg-green-100 text-green-800' : 
                        sample.confidence_score >= 0.6 ? 
                          'bg-yellow-100 text-yellow-800' : 
                          'bg-red-100 text-red-800'
                      }
                    >
                      {Math.round(sample.confidence_score * 100)}% confiance
                    </Badge>
                  </div>
                </div>
              ))}
            </div>
          </div>

          {/* Indicateurs de santé */}
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div className="p-4 bg-white rounded-lg border">
              <div className="flex items-center gap-2 mb-2">
                <TrendingUp className="h-4 w-4 text-green-500" />
                <span className="font-medium">Performance Globale</span>
              </div>
              <div className="space-y-2 text-sm">
                <div className="flex justify-between">
                  <span>Taux de succès:</span>
                  <span className="font-medium">{Math.round(report.statistics.success_rate * 100)}%</span>
                </div>
                <div className="flex justify-between">
                  <span>Confiance moyenne:</span>
                  <span className="font-medium">{Math.round(report.avg_confidence_score * 100)}%</span>
                </div>
                <div className="flex justify-between">
                  <span>Pages uniques:</span>
                  <span className="font-medium">{report.quality_indicators.unique_pages}</span>
                </div>
              </div>
            </div>

            <div className="p-4 bg-white rounded-lg border">
              <div className="flex items-center gap-2 mb-2">
                <Activity className="h-4 w-4 text-blue-500" />
                <span className="font-medium">Surveillance Active</span>
              </div>
              <div className="space-y-2 text-sm">
                <div className="flex justify-between">
                  <span>Échecs récents:</span>
                  <span className={`font-medium ${report.recent_failures === 0 ? 'text-green-600' : 'text-red-600'}`}>
                    {report.recent_failures}
                  </span>
                </div>
                <div className="flex justify-between">
                  <span>Types d'erreurs:</span>
                  <span className="font-medium">{report.failure_types.length || 'Aucune'}</span>
                </div>
                <div className="flex justify-between">
                  <span>Statut monitoring:</span>
                  <Badge className="bg-green-100 text-green-800">
                    <Activity className="h-3 w-3 mr-1" />
                    Actif
                  </Badge>
                </div>
              </div>
            </div>
          </div>

          {/* Message de garantie */}
          <div className="bg-green-50 border border-green-200 rounded-lg p-4">
            <div className="flex items-start gap-2">
              <CheckCircle className="h-5 w-5 text-green-600 mt-0.5" />
              <div>
                <h4 className="font-semibold text-green-800">Garantie de Délivrabilité</h4>
                <p className="text-sm text-green-700 mt-1">
                  Toutes les visites sont vérifiées en temps réel avec des navigateurs authentiques. 
                  Chaque interaction est tracée et validée pour garantir une délivrabilité à 100%.
                </p>
              </div>
            </div>
          </div>
        </CardContent>
      </Card>
    </div>
  );
}