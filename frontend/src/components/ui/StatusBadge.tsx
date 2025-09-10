'use client';

import { Badge } from '@/components/ui/badge';
import { cn } from '@/lib/utils';

interface StatusBadgeProps {
  status: 'pending' | 'running' | 'paused' | 'completed' | 'failed' | 'timeout';
  variant?: 'default' | 'secondary' | 'destructive' | 'outline';
  className?: string;
}

export function StatusBadge({ status, variant = 'default', className }: StatusBadgeProps) {
  const getStatusConfig = () => {
    switch (status) {
      case 'pending':
        return {
          label: 'Pending',
          className: 'bg-yellow-100 text-yellow-800 hover:bg-yellow-200',
        };
      case 'running':
        return {
          label: 'Running',
          className: 'bg-blue-100 text-blue-800 hover:bg-blue-200',
        };
      case 'paused':
        return {
          label: 'Paused',
          className: 'bg-orange-100 text-orange-800 hover:bg-orange-200',
        };
      case 'completed':
        return {
          label: 'Completed',
          className: 'bg-green-100 text-green-800 hover:bg-green-200',
        };
      case 'failed':
        return {
          label: 'Failed',
          className: 'bg-red-100 text-red-800 hover:bg-red-200',
        };
      case 'timeout':
        return {
          label: 'Timeout',
          className: 'bg-gray-100 text-gray-800 hover:bg-gray-200',
        };
      default:
        return {
          label: 'Unknown',
          className: 'bg-gray-100 text-gray-800 hover:bg-gray-200',
        };
    }
  };

  const config = getStatusConfig();

  return (
    <Badge
      variant={variant}
      className={cn(config.className, className)}
    >
      {config.label}
    </Badge>
  );
}
