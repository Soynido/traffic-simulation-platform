'use client';

import { useState, useEffect } from 'react';
import { Alert, AlertDescription } from '@/components/ui/alert';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { 
  AlertTriangle, 
  XCircle, 
  Clock, 
  Wifi,
  Shield,
  Activity,
  X
} from 'lucide-react';
import { useToast } from '@/components/ui/toast';

interface FailedVisit {
  id: string;
  url: string;
  error_type: 'timeout' | 'blocked' | 'network' | 'forbidden' | 'not_found';
  error_message: string;
  timestamp: string;
  session_id: string;
  campaign_id: string;
  retry_count: number;
}

interface VisitAlertsProps {
  campaignId: string;
  onRetry?: (visitId: string) => void;
}

export function VisitAlerts({ campaignId, onRetry }: VisitAlertsProps) {
  const [failedVisits, setFailedVisits] = useState<FailedVisit[]>([]);
  const [dismissedAlerts, setDismissedAlerts] = useState<Set<string>>(new Set());
  const { error } = useToast();

  useEffect(() => {
    const checkFailedVisits = async () => {
      try {
        const response = await fetch(`/api/campaigns/${campaignId}/failed-visits`);
        const data = await response.json();
        
        const visits = Array.isArray(data) ? data : data.failed_visits || [];
        setFailedVisits(visits);
        
        // Notifier les nouvelles erreurs critiques
        const criticalErrors = visits.filter(v => 
          v.error_type === 'blocked' || v.error_type === 'forbidden'
        );
        
        if (criticalErrors.length > 0) {
          error(
            'Visites bloquées détectées',
            `${criticalErrors.length} URL(s) ont été bloquées ou interdites`
          );
        }
      } catch (err) {
        console.error('Erreur lors de la vérification des visites échouées:', err);
      }
    };

    checkFailedVisits();
    const interval = setInterval(checkFailedVisits, 15000); // Check every 15s
    return () => clearInterval(interval);
  }, [campaignId, error]);

  const getErrorIcon = (errorType: string) => {
    switch (errorType) {
      case 'timeout':
        return <Clock className="h-4 w-4" />;
      case 'blocked':
        return <Shield className="h-4 w-4" />;
      case 'network':
        return <Wifi className="h-4 w-4" />;
      case 'forbidden':
        return <XCircle className="h-4 w-4" />;
      case 'not_found':
        return <AlertTriangle className="h-4 w-4" />;
      default:
        return <AlertTriangle className="h-4 w-4" />;
    }
  };

  const getErrorColor = (errorType: string) => {
    switch (errorType) {
      case 'timeout':
        return 'text-yellow-600 bg-yellow-50 border-yellow-200';
      case 'blocked':
      case 'forbidden':
        return 'text-red-600 bg-red-50 border-red-200';
      case 'network':
        return 'text-blue-600 bg-blue-50 border-blue-200';
      case 'not_found':
        return 'text-orange-600 bg-orange-50 border-orange-200';
      default:
        return 'text-gray-600 bg-gray-50 border-gray-200';
    }
  };

  const getErrorTitle = (errorType: string) => {
    switch (errorType) {
      case 'timeout':
        return 'Timeout de connexion';
      case 'blocked':
        return 'Visite bloquée';
      case 'network':
        return 'Erreur réseau';
      case 'forbidden':
        return 'Accès interdit';
      case 'not_found':
        return 'Page non trouvée';
      default:
        return 'Erreur inconnue';
    }
  };

  const handleDismiss = (visitId: string) => {
    setDismissedAlerts(prev => new Set([...prev, visitId]));
  };

  const handleRetry = async (visitId: string) => {
    if (onRetry) {
      onRetry(visitId);
    } else {
      // Retry logic par défaut
      try {
        await fetch(`/api/visits/${visitId}/retry`, { method: 'POST' });
        // Refresh the failed visits
        const response = await fetch(`/api/campaigns/${campaignId}/failed-visits`);
        const data = await response.json();
        setFailedVisits(Array.isArray(data) ? data : data.failed_visits || []);
      } catch (err) {
        console.error('Erreur lors de la nouvelle tentative:', err);
      }
    }
  };

  const visibleFailedVisits = failedVisits.filter(visit => !dismissedAlerts.has(visit.id));

  if (visibleFailedVisits.length === 0) {
    return null;
  }

  return (
    <div className="space-y-4">
      <div className="flex items-center justify-between">
        <h3 className="font-semibold text-red-600 flex items-center gap-2">
          <AlertTriangle className="h-5 w-5" />
          Alertes de Visites Échouées ({visibleFailedVisits.length})
        </h3>
        <Badge variant="destructive" className="animate-pulse">
          <Activity className="h-3 w-3 mr-1" />
          Surveillance Active
        </Badge>
      </div>

      <div className="space-y-3">
        {visibleFailedVisits.slice(0, 10).map((visit) => (
          <Alert
            key={visit.id}
            className={getErrorColor(visit.error_type)}
          >
            <div className="flex items-start justify-between w-full">
              <div className="flex items-start space-x-3 flex-1">
                {getErrorIcon(visit.error_type)}
                <div className="flex-1 min-w-0">
                  <div className="flex items-center space-x-2 mb-1">
                    <h4 className="font-medium">{getErrorTitle(visit.error_type)}</h4>
                    <Badge variant="outline" className="text-xs">
                      Tentative #{visit.retry_count + 1}
                    </Badge>
                  </div>
                  <AlertDescription className="space-y-2">
                    <div>
                      <p className="font-mono text-sm break-all">{visit.url}</p>
                      <p className="text-sm text-muted-foreground mt-1">
                        {visit.error_message}
                      </p>
                      <p className="text-xs text-muted-foreground">
                        {new Date(visit.timestamp).toLocaleString()}
                      </p>
                    </div>
                  </AlertDescription>
                </div>
              </div>
              
              <div className="flex items-center space-x-2 ml-4">
                {visit.error_type === 'timeout' || visit.error_type === 'network' ? (
                  <Button
                    size="sm"
                    variant="outline"
                    onClick={() => handleRetry(visit.id)}
                    disabled={visit.retry_count >= 3}
                  >
                    Réessayer
                  </Button>
                ) : null}
                <Button
                  size="sm"
                  variant="ghost"
                  onClick={() => handleDismiss(visit.id)}
                >
                  <X className="h-4 w-4" />
                </Button>
              </div>
            </div>
          </Alert>
        ))}
      </div>

      {/* Statistiques rapides */}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-4 pt-4 border-t">
        {['timeout', 'blocked', 'network', 'forbidden'].map(type => {
          const count = failedVisits.filter(v => v.error_type === type).length;
          if (count === 0) return null;
          
          return (
            <div key={type} className="text-center">
              <div className={`inline-flex items-center gap-1 px-2 py-1 rounded text-sm ${getErrorColor(type)}`}>
                {getErrorIcon(type)}
                <span className="font-medium">{count}</span>
              </div>
              <p className="text-xs text-muted-foreground mt-1 capitalize">
                {getErrorTitle(type).toLowerCase()}
              </p>
            </div>
          );
        })}
      </div>
    </div>
  );
}