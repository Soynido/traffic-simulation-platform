'use client';

import { ReactNode } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { TrendingUp, TrendingDown, Minus } from 'lucide-react';
import { cn } from '@/lib/utils';

interface KPICardProps {
  title: string;
  value: string | number;
  change?: {
    value: number;
    period: string;
    isPercentage?: boolean;
  };
  status?: 'success' | 'warning' | 'error' | 'neutral';
  icon?: ReactNode;
  description?: string;
  loading?: boolean;
}

export function KPICard({
  title,
  value,
  change,
  status = 'neutral',
  icon,
  description,
  loading = false,
}: KPICardProps) {
  const getChangeIcon = () => {
    if (!change) return null;
    
    if (change.value > 0) return <TrendingUp className="h-3 w-3" />;
    if (change.value < 0) return <TrendingDown className="h-3 w-3" />;
    return <Minus className="h-3 w-3" />;
  };

  const getChangeColor = () => {
    if (!change) return 'text-muted-foreground';
    
    if (change.value > 0) return 'text-success';
    if (change.value < 0) return 'text-error';
    return 'text-muted-foreground';
  };

  const getBorderColor = () => {
    switch (status) {
      case 'success':
        return 'border-l-success';
      case 'warning':
        return 'border-l-warning';
      case 'error':
        return 'border-l-error';
      default:
        return 'border-l-primary';
    }
  };

  return (
    <Card className={cn('border-l-4', getBorderColor())}>
      <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
        <CardTitle className="text-sm font-medium text-muted-foreground">
          {title}
        </CardTitle>
        {icon && (
          <div className="h-4 w-4 text-muted-foreground">
            {icon}
          </div>
        )}
      </CardHeader>
      <CardContent>
        <div className="text-2xl font-bold">
          {loading ? (
            <div className="h-8 w-16 bg-muted animate-pulse rounded" />
          ) : (
            value
          )}
        </div>
        
        {description && (
          <p className="text-xs text-muted-foreground mt-1">
            {description}
          </p>
        )}
        
        {change && !loading && (
          <div className={cn(
            'flex items-center space-x-1 text-xs mt-2',
            getChangeColor()
          )}>
            {getChangeIcon()}
            <span>
              {change.value > 0 ? '+' : ''}{change.value}{change.isPercentage ? '%' : ''}
            </span>
            <span className="text-muted-foreground">
              vs {change.period}
            </span>
          </div>
        )}
      </CardContent>
    </Card>
  );
}