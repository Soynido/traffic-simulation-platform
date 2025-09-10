'use client';

import { useState } from 'react';
import { useForm } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import * as z from 'zod';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Textarea } from '@/components/ui/textarea';
import { Switch } from '@/components/ui/switch';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { cn } from '@/lib/utils';

const campaignSchema = z.object({
  name: z.string().min(1, 'Name is required').max(200, 'Name must be less than 200 characters'),
  description: z.string().optional(),
  target_url: z.string().url('Must be a valid URL'),
  total_sessions: z.number().min(1, 'Total sessions must be positive'),
  concurrent_sessions: z.number().min(1, 'Concurrent sessions must be positive'),
  persona_id: z.string().min(1, 'Persona is required'),
  rate_limit_delay_ms: z.number().min(100, 'Rate limit must be at least 100ms').default(1000),
  user_agent_rotation: z.boolean().default(true),
  respect_robots_txt: z.boolean().default(true),
}).refine((data) => data.concurrent_sessions <= data.total_sessions, {
  message: 'Concurrent sessions must be <= total sessions',
  path: ['concurrent_sessions'],
});

type CampaignFormData = z.infer<typeof campaignSchema>;

interface Persona {
  id: string;
  name: string;
}

interface CampaignFormProps {
  initialData?: Partial<CampaignFormData>;
  personas: Persona[];
  onSubmit: (data: CampaignFormData) => void;
  onCancel?: () => void;
  loading?: boolean;
  className?: string;
}

export function CampaignForm({ 
  initialData, 
  personas,
  onSubmit, 
  onCancel, 
  loading = false,
  className 
}: CampaignFormProps) {
  const [isSubmitting, setIsSubmitting] = useState(false);

  const {
    register,
    handleSubmit,
    formState: { errors },
    watch,
    setValue,
  } = useForm<CampaignFormData>({
    resolver: zodResolver(campaignSchema),
    defaultValues: {
      name: initialData?.name || '',
      description: initialData?.description || '',
      target_url: initialData?.target_url || '',
      total_sessions: initialData?.total_sessions || 100,
      concurrent_sessions: initialData?.concurrent_sessions || 10,
      persona_id: initialData?.persona_id || '',
      rate_limit_delay_ms: initialData?.rate_limit_delay_ms || 1000,
      user_agent_rotation: initialData?.user_agent_rotation ?? true,
      respect_robots_txt: initialData?.respect_robots_txt ?? true,
    },
  });

  const totalSessions = watch('total_sessions');

  const handleFormSubmit = async (data: CampaignFormData) => {
    setIsSubmitting(true);
    try {
      await onSubmit(data);
    } finally {
      setIsSubmitting(false);
    }
  };

  return (
    <Card className={cn('w-full max-w-2xl', className)}>
      <CardHeader>
        <CardTitle>
          {initialData ? 'Edit Campaign' : 'Create New Campaign'}
        </CardTitle>
      </CardHeader>
      <CardContent>
        <form onSubmit={handleSubmit(handleFormSubmit)} className="space-y-6">
          {/* Basic Information */}
          <div className="space-y-4">
            <h3 className="text-lg font-medium">Basic Information</h3>
            
            <div className="space-y-4">
              <div className="space-y-2">
                <Label htmlFor="name">Campaign Name *</Label>
                <Input
                  id="name"
                  {...register('name')}
                  placeholder="e.g., Q1 Marketing Campaign"
                  className={errors.name ? 'border-red-500' : ''}
                />
                {errors.name && (
                  <p className="text-sm text-red-500">{errors.name.message}</p>
                )}
              </div>
              
              <div className="space-y-2">
                <Label htmlFor="description">Description</Label>
                <Textarea
                  id="description"
                  {...register('description')}
                  placeholder="Describe this campaign's purpose..."
                  rows={3}
                />
              </div>
              
              <div className="space-y-2">
                <Label htmlFor="target_url">Target URL *</Label>
                <Input
                  id="target_url"
                  {...register('target_url')}
                  placeholder="https://example.com"
                  className={errors.target_url ? 'border-red-500' : ''}
                />
                {errors.target_url && (
                  <p className="text-sm text-red-500">{errors.target_url.message}</p>
                )}
              </div>
            </div>
          </div>

          {/* Session Configuration */}
          <div className="space-y-4">
            <h3 className="text-lg font-medium">Session Configuration</h3>
            
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div className="space-y-2">
                <Label htmlFor="total_sessions">Total Sessions *</Label>
                <Input
                  id="total_sessions"
                  type="number"
                  {...register('total_sessions', { valueAsNumber: true })}
                  className={errors.total_sessions ? 'border-red-500' : ''}
                />
                {errors.total_sessions && (
                  <p className="text-sm text-red-500">{errors.total_sessions.message}</p>
                )}
              </div>
              
              <div className="space-y-2">
                <Label htmlFor="concurrent_sessions">Concurrent Sessions *</Label>
                <Input
                  id="concurrent_sessions"
                  type="number"
                  max={totalSessions}
                  {...register('concurrent_sessions', { valueAsNumber: true })}
                  className={errors.concurrent_sessions ? 'border-red-500' : ''}
                />
                {errors.concurrent_sessions && (
                  <p className="text-sm text-red-500">{errors.concurrent_sessions.message}</p>
                )}
                <p className="text-xs text-muted-foreground">
                  Maximum: {totalSessions}
                </p>
              </div>
            </div>
            
            <div className="space-y-2">
              <Label htmlFor="persona_id">Persona *</Label>
              <Select
                value={watch('persona_id')}
                onValueChange={(value) => setValue('persona_id', value)}
              >
                <SelectTrigger className={errors.persona_id ? 'border-red-500' : ''}>
                  <SelectValue placeholder="Select a persona" />
                </SelectTrigger>
                <SelectContent>
                  {personas.map((persona) => (
                    <SelectItem key={persona.id} value={persona.id}>
                      {persona.name}
                    </SelectItem>
                  ))}
                </SelectContent>
              </Select>
              {errors.persona_id && (
                <p className="text-sm text-red-500">{errors.persona_id.message}</p>
              )}
            </div>
          </div>

          {/* Advanced Configuration */}
          <div className="space-y-4">
            <h3 className="text-lg font-medium">Advanced Configuration</h3>
            
            <div className="space-y-4">
              <div className="space-y-2">
                <Label htmlFor="rate_limit_delay_ms">Rate Limit Delay (ms)</Label>
                <Input
                  id="rate_limit_delay_ms"
                  type="number"
                  min="100"
                  {...register('rate_limit_delay_ms', { valueAsNumber: true })}
                  className={errors.rate_limit_delay_ms ? 'border-red-500' : ''}
                />
                {errors.rate_limit_delay_ms && (
                  <p className="text-sm text-red-500">{errors.rate_limit_delay_ms.message}</p>
                )}
                <p className="text-xs text-muted-foreground">
                  Delay between requests to avoid overwhelming the target server
                </p>
              </div>
              
              <div className="flex items-center justify-between">
                <div className="space-y-0.5">
                  <Label htmlFor="user_agent_rotation">User Agent Rotation</Label>
                  <p className="text-sm text-muted-foreground">
                    Rotate user agents to appear more natural
                  </p>
                </div>
                <Switch
                  id="user_agent_rotation"
                  checked={watch('user_agent_rotation')}
                  onCheckedChange={(checked) => setValue('user_agent_rotation', checked)}
                />
              </div>
              
              <div className="flex items-center justify-between">
                <div className="space-y-0.5">
                  <Label htmlFor="respect_robots_txt">Respect robots.txt</Label>
                  <p className="text-sm text-muted-foreground">
                    Check and respect robots.txt file
                  </p>
                </div>
                <Switch
                  id="respect_robots_txt"
                  checked={watch('respect_robots_txt')}
                  onCheckedChange={(checked) => setValue('respect_robots_txt', checked)}
                />
              </div>
            </div>
          </div>

          {/* Form Actions */}
          <div className="flex justify-end space-x-2">
            {onCancel && (
              <Button
                type="button"
                variant="outline"
                onClick={onCancel}
                disabled={isSubmitting || loading}
              >
                Cancel
              </Button>
            )}
            <Button
              type="submit"
              disabled={isSubmitting || loading}
            >
              {isSubmitting || loading ? 'Saving...' : (initialData ? 'Update' : 'Create')}
            </Button>
          </div>
        </form>
      </CardContent>
    </Card>
  );
}
