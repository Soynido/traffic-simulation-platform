'use client';

import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, Legend } from 'recharts';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { cn } from '@/lib/utils';

interface ComparisonData {
  metric: string;
  human: number;
  simulated: number;
  difference?: number;
}

interface ComparisonChartProps {
  data: ComparisonData[];
  className?: string;
  title?: string;
  height?: number;
}

export function ComparisonChart({ 
  data, 
  className, 
  title = 'Human vs Simulated Comparison',
  height = 400 
}: ComparisonChartProps) {
  return (
    <Card className={cn('w-full', className)}>
      <CardHeader>
        <CardTitle className="text-lg font-semibold">{title}</CardTitle>
      </CardHeader>
      <CardContent>
        <ResponsiveContainer width="100%" height={height}>
          <BarChart data={data} margin={{ top: 20, right: 30, left: 20, bottom: 5 }}>
            <CartesianGrid strokeDasharray="3 3" className="opacity-30" />
            <XAxis 
              dataKey="metric" 
              tick={{ fontSize: 12 }}
              angle={-45}
              textAnchor="end"
              height={80}
            />
            <YAxis tick={{ fontSize: 12 }} />
            <Tooltip 
              formatter={(value, name) => [
                typeof value === 'number' ? value.toFixed(2) : value,
                name === 'human' ? 'Human Traffic' : 
                name === 'simulated' ? 'Simulated Traffic' : 'Difference'
              ]}
            />
            <Legend />
            <Bar 
              dataKey="human" 
              fill="#3b82f6" 
              name="Human Traffic"
              radius={[2, 2, 0, 0]}
            />
            <Bar 
              dataKey="simulated" 
              fill="#10b981" 
              name="Simulated Traffic"
              radius={[2, 2, 0, 0]}
            />
          </BarChart>
        </ResponsiveContainer>
        
        <div className="mt-4 grid grid-cols-1 md:grid-cols-3 gap-4">
          <div className="text-center p-3 bg-blue-50 rounded-lg">
            <div className="text-2xl font-bold text-blue-600">
              {data.reduce((sum, item) => sum + item.human, 0).toFixed(0)}
            </div>
            <div className="text-sm text-blue-600">Total Human</div>
          </div>
          <div className="text-center p-3 bg-green-50 rounded-lg">
            <div className="text-2xl font-bold text-green-600">
              {data.reduce((sum, item) => sum + item.simulated, 0).toFixed(0)}
            </div>
            <div className="text-sm text-green-600">Total Simulated</div>
          </div>
          <div className="text-center p-3 bg-gray-50 rounded-lg">
            <div className="text-2xl font-bold text-gray-600">
              {data.reduce((sum, item) => {
                const diff = item.simulated - item.human;
                return sum + Math.abs(diff);
              }, 0).toFixed(0)}
            </div>
            <div className="text-sm text-gray-600">Total Difference</div>
          </div>
        </div>
      </CardContent>
    </Card>
  );
}
