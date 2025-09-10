'use client';

import { useState, useEffect } from 'react';
import { PersonaTable } from '@/components/personas/PersonaTable';
import { PersonaForm } from '@/components/personas/PersonaForm';
import { Button } from '@/components/ui/button';
import { Dialog, DialogContent, DialogHeader, DialogTitle } from '@/components/ui/dialog';
import { Plus } from 'lucide-react';
import { 
  listPersonas, 
  createPersona, 
  updatePersona, 
  deletePersona,
  type Persona as APIPersona 
} from '@/services/api';
import { useToast } from '@/components/ui/toast';

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
  const { success, error } = useToast();

  // Fetch real data from API
  useEffect(() => {
    const fetchPersonas = async () => {
      setLoading(true);
      try {
        const response = await listPersonas({ page: 1, limit: 1000 });
        const personaItems = Array.isArray(response) ? response : (response?.items || []);
        setPersonas(personaItems as Persona[]);
      } catch (error) {
        console.error('Failed to fetch personas:', error);
        setPersonas([]);
      } finally {
        setLoading(false);
      }
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
    if (confirm(`Êtes-vous sûr de vouloir supprimer "${persona.name}" ?`)) {
      try {
        await deletePersona(persona.id);
        setPersonas(prev => prev.filter(p => p.id !== persona.id));
        success('Persona supprimé', `"${persona.name}" a été supprimé avec succès`);
      } catch (err) {
        console.error('Failed to delete persona:', err);
        error('Erreur', 'Impossible de supprimer le persona. Veuillez réessayer.');
      }
    }
  };

  const handleFormSubmit = async (data: any) => {
    try {
      if (editingPersona) {
        // Update existing persona
        const updatedPersona = await updatePersona(editingPersona.id, data);
        setPersonas(prev => prev.map(p => 
          p.id === editingPersona.id ? updatedPersona as Persona : p
        ));
        success('Persona modifié', `"${data.name || editingPersona.name}" a été mis à jour`);
      } else {
        // Create new persona
        const newPersona = await createPersona(data);
        setPersonas(prev => [...prev, newPersona as Persona]);
        success('Persona créé', `"${data.name}" a été créé avec succès`);
      }
      
      setShowForm(false);
      setEditingPersona(null);
    } catch (err) {
      console.error('Failed to save persona:', err);
      error('Erreur', 'Impossible de sauvegarder le persona. Veuillez réessayer.');
    }
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
