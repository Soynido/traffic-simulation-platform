'use client';

import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, Legend } from 'recharts';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { cn } from '@/lib/utils';

interface SessionData {
  timestamp: string;
  sessions: number;
  completed: number;
  failed: number;
}

interface SessionChartProps {
  data: SessionData[];
  className?: string;
  title?: string;
  height?: number;
}

export function SessionChart({ 
  data, 
  className, 
  title = 'Session Timeline',
  height = 300 
}: SessionChartProps) {
  return (
    <Card className={cn('w-full', className)}>
      <CardHeader>
        <CardTitle className="text-lg font-semibold">{title}</CardTitle>
      </CardHeader>
      <CardContent>
        <ResponsiveContainer width="100%" height={height}>
          <LineChart data={data} margin={{ top: 5, right: 30, left: 20, bottom: 5 }}>
            <CartesianGrid strokeDasharray="3 3" className="opacity-30" />
            <XAxis 
              dataKey="timestamp" 
              tick={{ fontSize: 12 }}
              tickFormatter={(value) => new Date(value).toLocaleTimeString()}
            />
            <YAxis tick={{ fontSize: 12 }} />
            <Tooltip 
              labelFormatter={(value) => new Date(value).toLocaleString()}
              formatter={(value, name) => [
                value,
                name === 'sessions' ? 'Total Sessions' : 
                name === 'completed' ? 'Completed' : 'Failed'
              ]}
            />
            <Legend />
            <Line
              type="monotone"
              dataKey="sessions"
              stroke="#3b82f6"
              strokeWidth={2}
              dot={{ r: 4 }}
              name="Total Sessions"
            />
            <Line
              type="monotone"
              dataKey="completed"
              stroke="#10b981"
              strokeWidth={2}
              dot={{ r: 4 }}
              name="Completed"
            />
            <Line
              type="monotone"
              dataKey="failed"
              stroke="#ef4444"
              strokeWidth={2}
              dot={{ r: 4 }}
              name="Failed"
            />
          </LineChart>
        </ResponsiveContainer>
      </CardContent>
    </Card>
  );
}
