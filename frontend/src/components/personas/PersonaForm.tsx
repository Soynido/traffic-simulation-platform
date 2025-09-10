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
import { cn } from '@/lib/utils';

const personaSchema = z.object({
  name: z.string().min(1, 'Name is required').max(100, 'Name must be less than 100 characters'),
  description: z.string().optional(),
  session_duration_min: z.number().min(1, 'Minimum duration must be positive'),
  session_duration_max: z.number().min(1, 'Maximum duration must be positive'),
  pages_min: z.number().min(1, 'Minimum pages must be positive'),
  pages_max: z.number().min(1, 'Maximum pages must be positive'),
  actions_per_page_min: z.number().min(1, 'Minimum actions must be positive').default(1),
  actions_per_page_max: z.number().min(1, 'Maximum actions must be positive').default(10),
  scroll_probability: z.number().min(0, 'Probability must be between 0 and 1').max(1, 'Probability must be between 0 and 1').default(0.8),
  click_probability: z.number().min(0, 'Probability must be between 0 and 1').max(1, 'Probability must be between 0 and 1').default(0.6),
  typing_probability: z.number().min(0, 'Probability must be between 0 and 1').max(1, 'Probability must be between 0 and 1').default(0.1),
}).refine((data) => data.session_duration_max >= data.session_duration_min, {
  message: 'Maximum duration must be >= minimum duration',
  path: ['session_duration_max'],
}).refine((data) => data.pages_max >= data.pages_min, {
  message: 'Maximum pages must be >= minimum pages',
  path: ['pages_max'],
}).refine((data) => data.actions_per_page_max >= data.actions_per_page_min, {
  message: 'Maximum actions must be >= minimum actions',
  path: ['actions_per_page_max'],
});

type PersonaFormData = z.infer<typeof personaSchema>;

interface PersonaFormProps {
  initialData?: Partial<PersonaFormData>;
  onSubmit: (data: PersonaFormData) => void;
  onCancel?: () => void;
  loading?: boolean;
  className?: string;
}

export function PersonaForm({ 
  initialData, 
  onSubmit, 
  onCancel, 
  loading = false,
  className 
}: PersonaFormProps) {
  const [isSubmitting, setIsSubmitting] = useState(false);

  const {
    register,
    handleSubmit,
    formState: { errors },
    watch,
  } = useForm<PersonaFormData>({
    resolver: zodResolver(personaSchema),
    defaultValues: {
      name: initialData?.name || '',
      description: initialData?.description || '',
      session_duration_min: initialData?.session_duration_min || 60,
      session_duration_max: initialData?.session_duration_max || 120,
      pages_min: initialData?.pages_min || 1,
      pages_max: initialData?.pages_max || 5,
      actions_per_page_min: initialData?.actions_per_page_min || 1,
      actions_per_page_max: initialData?.actions_per_page_max || 10,
      scroll_probability: initialData?.scroll_probability || 0.8,
      click_probability: initialData?.click_probability || 0.6,
      typing_probability: initialData?.typing_probability || 0.1,
    },
  });

  const handleFormSubmit = async (data: PersonaFormData) => {
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
          {initialData ? 'Edit Persona' : 'Create New Persona'}
        </CardTitle>
      </CardHeader>
      <CardContent>
        <form onSubmit={handleSubmit(handleFormSubmit)} className="space-y-6">
          {/* Basic Information */}
          <div className="space-y-4">
            <h3 className="text-lg font-medium">Basic Information</h3>
            
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div className="space-y-2">
                <Label htmlFor="name">Name *</Label>
                <Input
                  id="name"
                  {...register('name')}
                  placeholder="e.g., Rapid Visitor"
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
                  placeholder="Describe this persona's behavior..."
                  rows={3}
                />
              </div>
            </div>
          </div>

          {/* Session Configuration */}
          <div className="space-y-4">
            <h3 className="text-lg font-medium">Session Configuration</h3>
            
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div className="space-y-2">
                <Label htmlFor="session_duration_min">Min Duration (seconds) *</Label>
                <Input
                  id="session_duration_min"
                  type="number"
                  {...register('session_duration_min', { valueAsNumber: true })}
                  className={errors.session_duration_min ? 'border-red-500' : ''}
                />
                {errors.session_duration_min && (
                  <p className="text-sm text-red-500">{errors.session_duration_min.message}</p>
                )}
              </div>
              
              <div className="space-y-2">
                <Label htmlFor="session_duration_max">Max Duration (seconds) *</Label>
                <Input
                  id="session_duration_max"
                  type="number"
                  {...register('session_duration_max', { valueAsNumber: true })}
                  className={errors.session_duration_max ? 'border-red-500' : ''}
                />
                {errors.session_duration_max && (
                  <p className="text-sm text-red-500">{errors.session_duration_max.message}</p>
                )}
              </div>
            </div>
            
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div className="space-y-2">
                <Label htmlFor="pages_min">Min Pages *</Label>
                <Input
                  id="pages_min"
                  type="number"
                  {...register('pages_min', { valueAsNumber: true })}
                  className={errors.pages_min ? 'border-red-500' : ''}
                />
                {errors.pages_min && (
                  <p className="text-sm text-red-500">{errors.pages_min.message}</p>
                )}
              </div>
              
              <div className="space-y-2">
                <Label htmlFor="pages_max">Max Pages *</Label>
                <Input
                  id="pages_max"
                  type="number"
                  {...register('pages_max', { valueAsNumber: true })}
                  className={errors.pages_max ? 'border-red-500' : ''}
                />
                {errors.pages_max && (
                  <p className="text-sm text-red-500">{errors.pages_max.message}</p>
                )}
              </div>
            </div>
          </div>

          {/* Action Configuration */}
          <div className="space-y-4">
            <h3 className="text-lg font-medium">Action Configuration</h3>
            
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div className="space-y-2">
                <Label htmlFor="actions_per_page_min">Min Actions per Page</Label>
                <Input
                  id="actions_per_page_min"
                  type="number"
                  {...register('actions_per_page_min', { valueAsNumber: true })}
                  className={errors.actions_per_page_min ? 'border-red-500' : ''}
                />
                {errors.actions_per_page_min && (
                  <p className="text-sm text-red-500">{errors.actions_per_page_min.message}</p>
                )}
              </div>
              
              <div className="space-y-2">
                <Label htmlFor="actions_per_page_max">Max Actions per Page</Label>
                <Input
                  id="actions_per_page_max"
                  type="number"
                  {...register('actions_per_page_max', { valueAsNumber: true })}
                  className={errors.actions_per_page_max ? 'border-red-500' : ''}
                />
                {errors.actions_per_page_max && (
                  <p className="text-sm text-red-500">{errors.actions_per_page_max.message}</p>
                )}
              </div>
            </div>
          </div>

          {/* Behavioral Probabilities */}
          <div className="space-y-4">
            <h3 className="text-lg font-medium">Behavioral Probabilities</h3>
            
            <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
              <div className="space-y-2">
                <Label htmlFor="scroll_probability">Scroll Probability</Label>
                <Input
                  id="scroll_probability"
                  type="number"
                  step="0.01"
                  min="0"
                  max="1"
                  {...register('scroll_probability', { valueAsNumber: true })}
                  className={errors.scroll_probability ? 'border-red-500' : ''}
                />
                {errors.scroll_probability && (
                  <p className="text-sm text-red-500">{errors.scroll_probability.message}</p>
                )}
              </div>
              
              <div className="space-y-2">
                <Label htmlFor="click_probability">Click Probability</Label>
                <Input
                  id="click_probability"
                  type="number"
                  step="0.01"
                  min="0"
                  max="1"
                  {...register('click_probability', { valueAsNumber: true })}
                  className={errors.click_probability ? 'border-red-500' : ''}
                />
                {errors.click_probability && (
                  <p className="text-sm text-red-500">{errors.click_probability.message}</p>
                )}
              </div>
              
              <div className="space-y-2">
                <Label htmlFor="typing_probability">Typing Probability</Label>
                <Input
                  id="typing_probability"
                  type="number"
                  step="0.01"
                  min="0"
                  max="1"
                  {...register('typing_probability', { valueAsNumber: true })}
                  className={errors.typing_probability ? 'border-red-500' : ''}
                />
                {errors.typing_probability && (
                  <p className="text-sm text-red-500">{errors.typing_probability.message}</p>
                )}
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
