'use client';

import { Badge } from '@/components/ui/badge';
import { cn } from '@/lib/utils';
import { 
  Clock, 
  Play, 
  Pause, 
  CheckCircle, 
  AlertCircle, 
  Timer,
  Circle
} from 'lucide-react';

interface StatusBadgeProps {
  status: 'pending' | 'running' | 'paused' | 'completed' | 'failed' | 'timeout';
  variant?: 'default' | 'secondary' | 'destructive' | 'outline';
  className?: string;
  showIcon?: boolean;
}

export function StatusBadge({ status, variant = 'default', className, showIcon = true }: StatusBadgeProps) {
  const getStatusConfig = () => {
    switch (status) {
      case 'pending':
        return {
          label: 'Pending',
          icon: Clock,
          className: 'bg-yellow-100 text-yellow-800 hover:bg-yellow-200 border-yellow-300',
        };
      case 'running':
        return {
          label: 'Running',
          icon: Play,
          className: 'bg-green-100 text-green-800 hover:bg-green-200 border-green-300 animate-pulse',
        };
      case 'paused':
        return {
          label: 'Paused',
          icon: Pause,
          className: 'bg-orange-100 text-orange-800 hover:bg-orange-200 border-orange-300',
        };
      case 'completed':
        return {
          label: 'Completed',
          icon: CheckCircle,
          className: 'bg-blue-100 text-blue-800 hover:bg-blue-200 border-blue-300',
        };
      case 'failed':
        return {
          label: 'Failed',
          icon: AlertCircle,
          className: 'bg-red-100 text-red-800 hover:bg-red-200 border-red-300',
        };
      case 'timeout':
        return {
          label: 'Timeout',
          icon: Timer,
          className: 'bg-gray-100 text-gray-800 hover:bg-gray-200 border-gray-300',
        };
      default:
        return {
          label: 'Unknown',
          icon: Circle,
          className: 'bg-gray-100 text-gray-800 hover:bg-gray-200 border-gray-300',
        };
    }
  };

  const config = getStatusConfig();
  const IconComponent = config.icon;

  return (
    <Badge
      variant={variant}
      className={cn('flex items-center gap-1 border', config.className, className)}
    >
      {showIcon && <IconComponent className="h-3 w-3" />}
      {config.label}
    </Badge>
  );
}
