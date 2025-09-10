'use client';

import { useState, useEffect } from 'react';
import { CampaignTable } from '@/components/campaigns/CampaignTable';
import { CampaignForm } from '@/components/campaigns/CampaignForm';
import { CampaignProgressBar } from '@/components/campaigns/CampaignProgressBar';
import { LiveActivityLogs } from '@/components/campaigns/LiveActivityLogs';
import { DeliverabilityDashboard } from '@/components/campaigns/DeliverabilityDashboard';
import { VisitVerificationDashboard } from '@/components/campaigns/VisitVerificationDashboard';
import { Button } from '@/components/ui/button';
import { Dialog, DialogContent, DialogHeader, DialogTitle } from '@/components/ui/dialog';
import { Plus } from 'lucide-react';
import { 
  listCampaigns, 
  createCampaign, 
  updateCampaign, 
  deleteCampaign,
  startCampaign,
  pauseCampaign, 
  resumeCampaign,
  stopCampaign,
  type Campaign as APICampaign 
} from '@/services/campaigns';
import { listPersonas, type Persona } from '@/services/api';
import { useToast } from '@/components/ui/toast';

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

export default function CampaignsPage() {
  const [campaigns, setCampaigns] = useState<Campaign[]>([]);
  const [personas, setPersonas] = useState<Persona[]>([]);
  const [loading, setLoading] = useState(true);
  const [showForm, setShowForm] = useState(false);
  const [editingCampaign, setEditingCampaign] = useState<Campaign | null>(null);
  const { success, error } = useToast();

  // Fetch real data from API
  useEffect(() => {
    const fetchData = async () => {
      setLoading(true);
      try {
        const [campaignsRes, personasRes] = await Promise.all([
          listCampaigns({ page: 1, limit: 100 }),
          listPersonas({ page: 1, limit: 100 })
        ]);

        // Handle campaigns response
        let campaignItems: APICampaign[] = [];
        if (Array.isArray(campaignsRes)) {
          campaignItems = campaignsRes;
        } else if (campaignsRes && 'items' in campaignsRes) {
          campaignItems = campaignsRes.items;
        }

        // Handle personas response  
        let personaItems: Persona[] = [];
        if (Array.isArray(personasRes)) {
          personaItems = personasRes;
        } else if (personasRes && 'items' in personasRes) {
          personaItems = personasRes.items;
        }

        // Transform campaigns to include persona name
        const campaignsWithPersonaNames = campaignItems.map(campaign => ({
          ...campaign,
          persona_name: personaItems.find(p => p.id === campaign.persona_id)?.name || 'Unknown',
        })) as Campaign[];

        setCampaigns(campaignsWithPersonaNames);
        setPersonas(personaItems);
      } catch (error) {
        console.error('Failed to fetch data:', error);
        // Fallback to empty arrays
        setCampaigns([]);
        setPersonas([]);
      } finally {
        setLoading(false);
      }
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
      try {
        await deleteCampaign(campaign.id);
        setCampaigns(prev => prev.filter(c => c.id !== campaign.id));
      } catch (err) {
        console.error('Failed to delete campaign:', err);
        error('Erreur', 'Impossible de supprimer la campagne. Veuillez réessayer.');
      }
    }
  };

  const handleStartCampaign = async (campaign: Campaign) => {
    // Check if campaign can be started
    if (campaign.status === 'running') {
      error('Campagne déjà active', `"${campaign.name}" est déjà en cours d'exécution`);
      return;
    }

    try {
      const updatedCampaign = await startCampaign(campaign.id);
      setCampaigns(prev => prev.map(c => 
        c.id === campaign.id 
          ? { ...c, ...updatedCampaign, persona_name: campaign.persona_name }
          : c
      ));
      success('Campagne démarrée', `"${campaign.name}" est maintenant active`);
    } catch (err: any) {
      console.error('Failed to start campaign:', err);
      const message = err?.message || 'Impossible de démarrer la campagne. Veuillez réessayer.';
      
      if (err?.status === 409) {
        error('Conflit', 'Cette campagne ne peut pas être démarrée dans son état actuel');
      } else {
        error('Erreur', message);
      }
    }
  };

  const handlePauseCampaign = async (campaign: Campaign) => {
    if (campaign.status !== 'running') {
      error('Action impossible', `"${campaign.name}" doit être en cours pour être mise en pause`);
      return;
    }

    try {
      const updatedCampaign = await pauseCampaign(campaign.id);
      setCampaigns(prev => prev.map(c => 
        c.id === campaign.id 
          ? { ...c, ...updatedCampaign, persona_name: campaign.persona_name }
          : c
      ));
      success('Campagne mise en pause', `"${campaign.name}" est maintenant en pause`);
    } catch (err: any) {
      console.error('Failed to pause campaign:', err);
      const message = err?.message || 'Impossible de mettre en pause la campagne.';
      error('Erreur', message);
    }
  };

  const handleResumeCampaign = async (campaign: Campaign) => {
    if (campaign.status !== 'paused') {
      error('Action impossible', `"${campaign.name}" doit être en pause pour être reprise`);
      return;
    }

    try {
      const updatedCampaign = await resumeCampaign(campaign.id);
      setCampaigns(prev => prev.map(c => 
        c.id === campaign.id 
          ? { ...c, ...updatedCampaign, persona_name: campaign.persona_name }
          : c
      ));
      success('Campagne reprise', `"${campaign.name}" est de nouveau active`);
    } catch (err: any) {
      console.error('Failed to resume campaign:', err);
      const message = err?.message || 'Impossible de reprendre la campagne.';
      error('Erreur', message);
    }
  };

  const handleStopCampaign = async (campaign: Campaign) => {
    if (!['running', 'paused'].includes(campaign.status)) {
      error('Action impossible', `"${campaign.name}" ne peut pas être arrêtée dans son état actuel`);
      return;
    }

    try {
      const updatedCampaign = await stopCampaign(campaign.id);
      setCampaigns(prev => prev.map(c => 
        c.id === campaign.id 
          ? { ...c, ...updatedCampaign, persona_name: campaign.persona_name }
          : c
      ));
      success('Campagne arrêtée', `"${campaign.name}" est maintenant terminée`);
    } catch (err: any) {
      console.error('Failed to stop campaign:', err);
      const message = err?.message || 'Impossible d\'arrêter la campagne.';
      error('Erreur', message);
    }
  };

  const handleFormSubmit = async (data: any) => {
    try {
      if (editingCampaign) {
        // Update existing campaign
        const updatedCampaign = await updateCampaign(editingCampaign.id, data);
        setCampaigns(prev => prev.map(c => 
          c.id === editingCampaign.id 
            ? { 
                ...c, 
                ...updatedCampaign, 
                persona_name: personas.find(p => p.id === updatedCampaign.persona_id)?.name || 'Unknown'
              }
            : c
        ));
        success('Campagne modifiée', `"${data.name || editingCampaign.name}" a été mise à jour`);
      } else {
        // Create new campaign
        const newCampaign = await createCampaign(data);
        const campaignWithPersonaName = {
          ...newCampaign,
          persona_name: personas.find(p => p.id === newCampaign.persona_id)?.name || 'Unknown'
        } as Campaign;
        setCampaigns(prev => [...prev, campaignWithPersonaName]);
        success('Campagne créée', `"${data.name}" a été créée avec succès`);
      }
      
      setShowForm(false);
      setEditingCampaign(null);
    } catch (err) {
      console.error('Failed to save campaign:', err);
      error('Erreur', 'Impossible de sauvegarder la campagne. Veuillez réessayer.');
    }
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

        {/* Active Campaign Progress avec Données Réelles */}
        {campaigns.filter(c => c.status === 'running').length > 0 && (
          <div className="space-y-6">
            <h2 className="text-xl font-semibold">Campagnes Actives - Suivi en Temps Réel</h2>
            
            {/* Progress bars avec vraies données */}
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
              {campaigns
                .filter(c => c.status === 'running')
                .map(campaign => (
                  <CampaignProgressBar
                    key={campaign.id}
                    campaignId={campaign.id}
                    campaignName={campaign.name}
                    status={campaign.status}
                    totalSessions={campaign.total_sessions}
                    targetUrl={campaign.target_url}
                  />
                ))}
            </div>

            {/* Dashboard de transparence pour la première campagne active */}
            {campaigns.filter(c => c.status === 'running').length > 0 && (
              <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
                <LiveActivityLogs
                  campaignId={campaigns.filter(c => c.status === 'running')[0].id}
                  campaignName={campaigns.filter(c => c.status === 'running')[0].name}
                  isRunning={true}
                />
                <DeliverabilityDashboard
                  campaignId={campaigns.filter(c => c.status === 'running')[0].id}
                  campaignName={campaigns.filter(c => c.status === 'running')[0].name}
                  campaignStatus={campaigns.filter(c => c.status === 'running')[0].status}
                />
              </div>
            )}

            {/* Vérification détaillée des visites */}
            {campaigns.filter(c => c.status === 'running').length > 0 && (
              <VisitVerificationDashboard
                campaignId={campaigns.filter(c => c.status === 'running')[0].id}
                campaignName={campaigns.filter(c => c.status === 'running')[0].name}
              />
            )}
          </div>
        )}

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
