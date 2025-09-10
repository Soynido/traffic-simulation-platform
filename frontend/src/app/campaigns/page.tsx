'use client';

import { useState, useEffect } from 'react';
import { CampaignTable } from '@/components/campaigns/CampaignTable';
import { CampaignForm } from '@/components/campaigns/CampaignForm';
import { Button } from '@/components/ui/button';
import { Dialog, DialogContent, DialogHeader, DialogTitle } from '@/components/ui/dialog';
import { Plus } from 'lucide-react';

interface Campaign {
  id: string;
  name: string;
  description?: string;
  target_url: string;
  total_sessions: number;
  concurrent_sessions: number;
  status: 'pending' | 'running' | 'paused' | 'completed' | 'failed';
  persona_id: string;
  persona_name?: string;
  rate_limit_delay_ms: number;
  user_agent_rotation: boolean;
  respect_robots_txt: boolean;
  created_at: string;
  updated_at: string;
  started_at?: string;
  completed_at?: string;
}

interface Persona {
  id: string;
  name: string;
}

export default function CampaignsPage() {
  const [campaigns, setCampaigns] = useState<Campaign[]>([]);
  const [personas, setPersonas] = useState<Persona[]>([]);
  const [loading, setLoading] = useState(true);
  const [showForm, setShowForm] = useState(false);
  const [editingCampaign, setEditingCampaign] = useState<Campaign | null>(null);

  // Mock data - in real app, this would come from API
  useEffect(() => {
    const fetchData = async () => {
      setLoading(true);
      // Simulate API call
      await new Promise(resolve => setTimeout(resolve, 1000));
      
      setPersonas([
        { id: '1', name: 'Rapid Visitor' },
        { id: '2', name: 'Careful Reader' },
        { id: '3', name: 'Social Browser' },
      ]);
      
      setCampaigns([
        {
          id: '1',
          name: 'Q1 Marketing Campaign',
          description: 'Traffic simulation for Q1 marketing pages',
          target_url: 'https://example.com/marketing',
          total_sessions: 1000,
          concurrent_sessions: 50,
          status: 'running',
          persona_id: '1',
          persona_name: 'Rapid Visitor',
          rate_limit_delay_ms: 1000,
          user_agent_rotation: true,
          respect_robots_txt: true,
          created_at: '2024-01-15T10:00:00Z',
          updated_at: '2024-01-15T10:00:00Z',
          started_at: '2024-01-15T10:30:00Z',
        },
        {
          id: '2',
          name: 'Product Demo Simulation',
          description: 'Simulate user behavior on product demo pages',
          target_url: 'https://example.com/demo',
          total_sessions: 500,
          concurrent_sessions: 25,
          status: 'paused',
          persona_id: '2',
          persona_name: 'Careful Reader',
          rate_limit_delay_ms: 1500,
          user_agent_rotation: true,
          respect_robots_txt: true,
          created_at: '2024-01-15T11:00:00Z',
          updated_at: '2024-01-15T11:00:00Z',
          started_at: '2024-01-15T11:15:00Z',
        },
        {
          id: '3',
          name: 'Social Media Campaign',
          description: 'Test social sharing features',
          target_url: 'https://example.com/social',
          total_sessions: 200,
          concurrent_sessions: 10,
          status: 'completed',
          persona_id: '3',
          persona_name: 'Social Browser',
          rate_limit_delay_ms: 800,
          user_agent_rotation: false,
          respect_robots_txt: true,
          created_at: '2024-01-15T12:00:00Z',
          updated_at: '2024-01-15T12:00:00Z',
          started_at: '2024-01-15T12:30:00Z',
          completed_at: '2024-01-15T14:30:00Z',
        },
      ]);
      setLoading(false);
    };

    fetchData();
  }, []);

  const handleCreateCampaign = () => {
    setEditingCampaign(null);
    setShowForm(true);
  };

  const handleEditCampaign = (campaign: Campaign) => {
    setEditingCampaign(campaign);
    setShowForm(true);
  };

  const handleDeleteCampaign = async (campaign: Campaign) => {
    if (confirm(`Are you sure you want to delete "${campaign.name}"?`)) {
      // Simulate API call
      setCampaigns(prev => prev.filter(c => c.id !== campaign.id));
    }
  };

  const handleStartCampaign = async (campaign: Campaign) => {
    // Simulate API call
    setCampaigns(prev => prev.map(c => 
      c.id === campaign.id 
        ? { ...c, status: 'running' as const, started_at: new Date().toISOString() }
        : c
    ));
  };

  const handlePauseCampaign = async (campaign: Campaign) => {
    // Simulate API call
    setCampaigns(prev => prev.map(c => 
      c.id === campaign.id 
        ? { ...c, status: 'paused' as const }
        : c
    ));
  };

  const handleResumeCampaign = async (campaign: Campaign) => {
    // Simulate API call
    setCampaigns(prev => prev.map(c => 
      c.id === campaign.id 
        ? { ...c, status: 'running' as const }
        : c
    ));
  };

  const handleStopCampaign = async (campaign: Campaign) => {
    // Simulate API call
    setCampaigns(prev => prev.map(c => 
      c.id === campaign.id 
        ? { ...c, status: 'completed' as const, completed_at: new Date().toISOString() }
        : c
    ));
  };

  const handleFormSubmit = async (data: any) => {
    // Simulate API call
    if (editingCampaign) {
      setCampaigns(prev => prev.map(c => 
        c.id === editingCampaign.id 
          ? { 
              ...c, 
              ...data, 
              persona_name: personas.find(p => p.id === data.persona_id)?.name,
              updated_at: new Date().toISOString() 
            }
          : c
      ));
    } else {
      const newCampaign: Campaign = {
        id: Date.now().toString(),
        ...data,
        persona_name: personas.find(p => p.id === data.persona_id)?.name,
        status: 'pending',
        created_at: new Date().toISOString(),
        updated_at: new Date().toISOString(),
      };
      setCampaigns(prev => [...prev, newCampaign]);
    }
    
    setShowForm(false);
    setEditingCampaign(null);
  };

  const handleFormCancel = () => {
    setShowForm(false);
    setEditingCampaign(null);
  };

  return (
    <div className="min-h-screen bg-background p-6">
      <div className="max-w-7xl mx-auto space-y-6">
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-3xl font-bold">Campaigns</h1>
            <p className="text-muted-foreground">
              Manage traffic simulation campaigns
            </p>
          </div>
          <Button onClick={handleCreateCampaign}>
            <Plus className="h-4 w-4 mr-2" />
            Create Campaign
          </Button>
        </div>

        <CampaignTable
          campaigns={campaigns}
          onEdit={handleEditCampaign}
          onDelete={handleDeleteCampaign}
          onCreate={handleCreateCampaign}
          onStart={handleStartCampaign}
          onPause={handlePauseCampaign}
          onResume={handleResumeCampaign}
          onStop={handleStopCampaign}
          loading={loading}
        />

        <Dialog open={showForm} onOpenChange={setShowForm}>
          <DialogContent className="max-w-4xl max-h-[90vh] overflow-y-auto">
            <DialogHeader>
              <DialogTitle>
                {editingCampaign ? 'Edit Campaign' : 'Create New Campaign'}
              </DialogTitle>
            </DialogHeader>
            <CampaignForm
              initialData={editingCampaign || undefined}
              personas={personas}
              onSubmit={handleFormSubmit}
              onCancel={handleFormCancel}
            />
          </DialogContent>
        </Dialog>
      </div>
    </div>
  );
}
