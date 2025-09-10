'use client';

import { useState, useEffect } from 'react';
import { PersonaTable } from '@/components/personas/PersonaTable';
import { PersonaForm } from '@/components/personas/PersonaForm';
import { Button } from '@/components/ui/button';
import { Dialog, DialogContent, DialogHeader, DialogTitle } from '@/components/ui/dialog';
import { Plus } from 'lucide-react';

interface Persona {
  id: string;
  name: string;
  description?: string;
  session_duration_min: number;
  session_duration_max: number;
  pages_min: number;
  pages_max: number;
  actions_per_page_min: number;
  actions_per_page_max: number;
  scroll_probability: number;
  click_probability: number;
  typing_probability: number;
  created_at: string;
  updated_at: string;
}

export default function PersonasPage() {
  const [personas, setPersonas] = useState<Persona[]>([]);
  const [loading, setLoading] = useState(true);
  const [showForm, setShowForm] = useState(false);
  const [editingPersona, setEditingPersona] = useState<Persona | null>(null);

  // Mock data - in real app, this would come from API
  useEffect(() => {
    const fetchPersonas = async () => {
      setLoading(true);
      // Simulate API call
      await new Promise(resolve => setTimeout(resolve, 1000));
      
      setPersonas([
        {
          id: '1',
          name: 'Rapid Visitor',
          description: 'Quick browser who skims content',
          session_duration_min: 30,
          session_duration_max: 90,
          pages_min: 1,
          pages_max: 3,
          actions_per_page_min: 2,
          actions_per_page_max: 5,
          scroll_probability: 0.6,
          click_probability: 0.4,
          typing_probability: 0.1,
          created_at: '2024-01-15T10:00:00Z',
          updated_at: '2024-01-15T10:00:00Z',
        },
        {
          id: '2',
          name: 'Careful Reader',
          description: 'Thorough reader who examines content carefully',
          session_duration_min: 120,
          session_duration_max: 300,
          pages_min: 3,
          pages_max: 8,
          actions_per_page_min: 5,
          actions_per_page_max: 15,
          scroll_probability: 0.9,
          click_probability: 0.7,
          typing_probability: 0.3,
          created_at: '2024-01-15T11:00:00Z',
          updated_at: '2024-01-15T11:00:00Z',
        },
        {
          id: '3',
          name: 'Social Browser',
          description: 'User who focuses on social features and sharing',
          session_duration_min: 60,
          session_duration_max: 180,
          pages_min: 2,
          pages_max: 5,
          actions_per_page_min: 3,
          actions_per_page_max: 8,
          scroll_probability: 0.7,
          click_probability: 0.8,
          typing_probability: 0.2,
          created_at: '2024-01-15T12:00:00Z',
          updated_at: '2024-01-15T12:00:00Z',
        },
      ]);
      setLoading(false);
    };

    fetchPersonas();
  }, []);

  const handleCreatePersona = () => {
    setEditingPersona(null);
    setShowForm(true);
  };

  const handleEditPersona = (persona: Persona) => {
    setEditingPersona(persona);
    setShowForm(true);
  };

  const handleDeletePersona = async (persona: Persona) => {
    if (confirm(`Are you sure you want to delete "${persona.name}"?`)) {
      // Simulate API call
      setPersonas(prev => prev.filter(p => p.id !== persona.id));
    }
  };

  const handleFormSubmit = async (data: any) => {
    // Simulate API call
    if (editingPersona) {
      setPersonas(prev => prev.map(p => 
        p.id === editingPersona.id 
          ? { ...p, ...data, updated_at: new Date().toISOString() }
          : p
      ));
    } else {
      const newPersona: Persona = {
        id: Date.now().toString(),
        ...data,
        created_at: new Date().toISOString(),
        updated_at: new Date().toISOString(),
      };
      setPersonas(prev => [...prev, newPersona]);
    }
    
    setShowForm(false);
    setEditingPersona(null);
  };

  const handleFormCancel = () => {
    setShowForm(false);
    setEditingPersona(null);
  };

  return (
    <div className="min-h-screen bg-background p-6">
      <div className="max-w-7xl mx-auto space-y-6">
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-3xl font-bold">Personas</h1>
            <p className="text-muted-foreground">
              Manage user behavior profiles for traffic simulation
            </p>
          </div>
          <Button onClick={handleCreatePersona}>
            <Plus className="h-4 w-4 mr-2" />
            Create Persona
          </Button>
        </div>

        <PersonaTable
          personas={personas}
          onEdit={handleEditPersona}
          onDelete={handleDeletePersona}
          onCreate={handleCreatePersona}
          loading={loading}
        />

        <Dialog open={showForm} onOpenChange={setShowForm}>
          <DialogContent className="max-w-4xl max-h-[90vh] overflow-y-auto">
            <DialogHeader>
              <DialogTitle>
                {editingPersona ? 'Edit Persona' : 'Create New Persona'}
              </DialogTitle>
            </DialogHeader>
            <PersonaForm
              initialData={editingPersona || undefined}
              onSubmit={handleFormSubmit}
              onCancel={handleFormCancel}
            />
          </DialogContent>
        </Dialog>
      </div>
    </div>
  );
}
