'use client';

import { Badge } from '@/components/ui/badge';
import { cn } from '@/lib/utils';

interface LiveIndicatorProps {
  isLive: boolean;
  className?: string;
  showText?: boolean;
}

export function LiveIndicator({ isLive, className, showText = true }: LiveIndicatorProps) {
  return (
    <div className={cn('flex items-center space-x-2', className)}>
      <div
        className={cn(
          'h-2 w-2 rounded-full',
          isLive
            ? 'bg-green-500 animate-pulse'
            : 'bg-gray-400'
        )}
      />
      {showText && (
        <Badge
          variant={isLive ? 'default' : 'secondary'}
          className={cn(
            isLive
              ? 'bg-green-100 text-green-800 hover:bg-green-200'
              : 'bg-gray-100 text-gray-800 hover:bg-gray-200'
          )}
        >
          {isLive ? 'Live' : 'Offline'}
        </Badge>
      )}
    </div>
  );
}
