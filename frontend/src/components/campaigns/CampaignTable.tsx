'use client';

import { useState } from 'react';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Input } from '@/components/ui/input';
import { Badge } from '@/components/ui/badge';
import { 
  Table, 
  TableBody, 
  TableCell, 
  TableHead, 
  TableHeader, 
  TableRow 
} from '@/components/ui/table';
import { 
  DropdownMenu, 
  DropdownMenuContent, 
  DropdownMenuItem, 
  DropdownMenuTrigger 
} from '@/components/ui/dropdown-menu';
import { 
  MoreHorizontal, 
  Edit, 
  Trash2, 
  Search,
  Plus,
  Filter,
  Play,
  Pause,
  Square,
  CheckCircle,
  AlertCircle
} from 'lucide-react';
import { StatusBadge } from '@/components/ui/StatusBadge';
import { cn } from '@/lib/utils';

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

interface CampaignTableProps {
  campaigns: Campaign[];
  onEdit?: (campaign: Campaign) => void;
  onDelete?: (campaign: Campaign) => void;
  onCreate?: () => void;
  onStart?: (campaign: Campaign) => void;
  onPause?: (campaign: Campaign) => void;
  onResume?: (campaign: Campaign) => void;
  onStop?: (campaign: Campaign) => void;
  loading?: boolean;
  className?: string;
}

export function CampaignTable({ 
  campaigns, 
  onEdit, 
  onDelete, 
  onCreate,
  onStart,
  onPause,
  onResume,
  onStop,
  loading = false,
  className 
}: CampaignTableProps) {
  const [searchTerm, setSearchTerm] = useState('');
  const [statusFilter, setStatusFilter] = useState<string>('all');
  const [sortBy, setSortBy] = useState<'name' | 'created_at' | 'status'>('created_at');
  const [sortOrder, setSortOrder] = useState<'asc' | 'desc'>('desc');

  const filteredCampaigns = campaigns
    .filter(campaign => {
      const matchesSearch = 
        campaign.name.toLowerCase().includes(searchTerm.toLowerCase()) ||
        (campaign.description && campaign.description.toLowerCase().includes(searchTerm.toLowerCase())) ||
        campaign.target_url.toLowerCase().includes(searchTerm.toLowerCase());
      
      const matchesStatus = statusFilter === 'all' || campaign.status === statusFilter;
      
      return matchesSearch && matchesStatus;
    })
    .sort((a, b) => {
      const aValue = a[sortBy];
      const bValue = b[sortBy];
      
      if (sortOrder === 'asc') {
        return aValue < bValue ? -1 : aValue > bValue ? 1 : 0;
      } else {
        return aValue > bValue ? -1 : aValue < bValue ? 1 : 0;
      }
    });

  const handleSort = (field: 'name' | 'created_at' | 'status') => {
    if (sortBy === field) {
      setSortOrder(sortOrder === 'asc' ? 'desc' : 'asc');
    } else {
      setSortBy(field);
      setSortOrder('asc');
    }
  };

  const formatDate = (dateString: string) => {
    return new Date(dateString).toLocaleDateString();
  };

  const getStatusActions = (campaign: Campaign) => {
    switch (campaign.status) {
      case 'pending':
        return onStart ? (
          <Button
            size="sm"
            onClick={() => onStart(campaign)}
            className="bg-green-600 hover:bg-green-700"
          >
            <Play className="h-4 w-4 mr-1" />
            Start
          </Button>
        ) : null;
      case 'running':
        return (
          <div className="flex space-x-1">
            {onPause && (
              <Button
                size="sm"
                variant="outline"
                onClick={() => onPause(campaign)}
                className="border-yellow-600 text-yellow-600 hover:bg-yellow-50"
              >
                <Pause className="h-4 w-4 mr-1" />
                Pause
              </Button>
            )}
            {onStop && (
              <Button
                size="sm"
                variant="outline"
                onClick={() => onStop(campaign)}
                className="border-red-600 text-red-600 hover:bg-red-50"
              >
                <Square className="h-4 w-4 mr-1" />
                Stop
              </Button>
            )}
          </div>
        );
      case 'paused':
        return (
          <div className="flex space-x-1">
            {onResume && (
              <Button
                size="sm"
                onClick={() => onResume(campaign)}
                className="bg-blue-600 hover:bg-blue-700"
              >
                <Play className="h-4 w-4 mr-1" />
                Resume
              </Button>
            )}
            {onStop && (
              <Button
                size="sm"
                variant="outline"
                onClick={() => onStop(campaign)}
                className="border-red-600 text-red-600 hover:bg-red-50"
              >
                <Square className="h-4 w-4 mr-1" />
                Stop
              </Button>
            )}
          </div>
        );
      case 'completed':
        return (
          <div className="text-sm text-green-600 font-medium flex items-center">
            <CheckCircle className="h-4 w-4 mr-1" />
            Completed
          </div>
        );
      case 'failed':
        return (
          <div className="text-sm text-red-600 font-medium flex items-center">
            <AlertCircle className="h-4 w-4 mr-1" />
            Failed
          </div>
        );
      default:
        return null;
    }
  };

  return (
    <Card className={cn('w-full', className)}>
      <CardHeader>
        <div className="flex items-center justify-between">
          <CardTitle>Campaigns</CardTitle>
          {onCreate && (
            <Button onClick={onCreate} size="sm">
              <Plus className="h-4 w-4 mr-2" />
              Create Campaign
            </Button>
          )}
        </div>
        
        <div className="flex items-center space-x-4">
          <div className="relative flex-1 max-w-sm">
            <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 h-4 w-4 text-muted-foreground" />
            <Input
              placeholder="Search campaigns..."
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
              className="pl-10"
            />
          </div>
          
          <DropdownMenu>
            <DropdownMenuTrigger asChild>
              <Button variant="outline" size="sm">
                <Filter className="h-4 w-4 mr-2" />
                Filter
              </Button>
            </DropdownMenuTrigger>
            <DropdownMenuContent>
              <DropdownMenuItem onClick={() => setStatusFilter('all')}>
                All Status
              </DropdownMenuItem>
              <DropdownMenuItem onClick={() => setStatusFilter('pending')}>
                Pending
              </DropdownMenuItem>
              <DropdownMenuItem onClick={() => setStatusFilter('running')}>
                Running
              </DropdownMenuItem>
              <DropdownMenuItem onClick={() => setStatusFilter('paused')}>
                Paused
              </DropdownMenuItem>
              <DropdownMenuItem onClick={() => setStatusFilter('completed')}>
                Completed
              </DropdownMenuItem>
              <DropdownMenuItem onClick={() => setStatusFilter('failed')}>
                Failed
              </DropdownMenuItem>
            </DropdownMenuContent>
          </DropdownMenu>
          
          <DropdownMenu>
            <DropdownMenuTrigger asChild>
              <Button variant="outline" size="sm">
                <Filter className="h-4 w-4 mr-2" />
                Sort
              </Button>
            </DropdownMenuTrigger>
            <DropdownMenuContent>
              <DropdownMenuItem onClick={() => handleSort('name')}>
                Name {sortBy === 'name' && (sortOrder === 'asc' ? '↑' : '↓')}
              </DropdownMenuItem>
              <DropdownMenuItem onClick={() => handleSort('status')}>
                Status {sortBy === 'status' && (sortOrder === 'asc' ? '↑' : '↓')}
              </DropdownMenuItem>
              <DropdownMenuItem onClick={() => handleSort('created_at')}>
                Created {sortBy === 'created_at' && (sortOrder === 'asc' ? '↑' : '↓')}
              </DropdownMenuItem>
            </DropdownMenuContent>
          </DropdownMenu>
        </div>
      </CardHeader>
      
      <CardContent>
        {loading ? (
          <div className="space-y-4">
            {[...Array(5)].map((_, i) => (
              <div key={i} className="h-16 bg-muted animate-pulse rounded" />
            ))}
          </div>
        ) : (
          <Table>
            <TableHeader>
              <TableRow>
                <TableHead>Name</TableHead>
                <TableHead>Status</TableHead>
                <TableHead>Target URL</TableHead>
                <TableHead>Sessions</TableHead>
                <TableHead>Persona</TableHead>
                <TableHead>Created</TableHead>
                <TableHead>Actions</TableHead>
                <TableHead className="w-[50px]"></TableHead>
              </TableRow>
            </TableHeader>
            <TableBody>
              {filteredCampaigns.length === 0 ? (
                <TableRow>
                  <TableCell colSpan={8} className="text-center py-8 text-muted-foreground">
                    {searchTerm || statusFilter !== 'all' 
                      ? 'No campaigns found matching your criteria.' 
                      : 'No campaigns created yet.'
                    }
                  </TableCell>
                </TableRow>
              ) : (
                filteredCampaigns.map((campaign) => (
                  <TableRow key={campaign.id}>
                    <TableCell className="font-medium">
                      <div>
                        <div className="font-medium">{campaign.name}</div>
                        {campaign.description && (
                          <div className="text-sm text-muted-foreground truncate max-w-xs">
                            {campaign.description}
                          </div>
                        )}
                      </div>
                    </TableCell>
                    <TableCell>
                      <StatusBadge status={campaign.status} />
                    </TableCell>
                    <TableCell className="max-w-xs">
                      <div className="text-sm text-blue-600 truncate">
                        {campaign.target_url}
                      </div>
                    </TableCell>
                    <TableCell>
                      <div className="text-sm">
                        {campaign.concurrent_sessions} / {campaign.total_sessions}
                      </div>
                    </TableCell>
                    <TableCell>
                      <div className="text-sm">
                        {campaign.persona_name || 'Unknown'}
                      </div>
                    </TableCell>
                    <TableCell className="text-sm text-muted-foreground">
                      {formatDate(campaign.created_at)}
                    </TableCell>
                    <TableCell>
                      {getStatusActions(campaign)}
                    </TableCell>
                    <TableCell>
                      <DropdownMenu>
                        <DropdownMenuTrigger asChild>
                          <Button variant="ghost" size="sm">
                            <MoreHorizontal className="h-4 w-4" />
                          </Button>
                        </DropdownMenuTrigger>
                        <DropdownMenuContent align="end">
                          {onEdit && (
                            <DropdownMenuItem onClick={() => onEdit(campaign)}>
                              <Edit className="h-4 w-4 mr-2" />
                              Edit
                            </DropdownMenuItem>
                          )}
                          {onDelete && (
                            <DropdownMenuItem 
                              onClick={() => onDelete(campaign)}
                              className="text-red-600"
                            >
                              <Trash2 className="h-4 w-4 mr-2" />
                              Delete
                            </DropdownMenuItem>
                          )}
                        </DropdownMenuContent>
                      </DropdownMenu>
                    </TableCell>
                  </TableRow>
                ))
              )}
            </TableBody>
          </Table>
        )}
      </CardContent>
    </Card>
  );
}
