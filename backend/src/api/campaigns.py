"""
Campaigns API endpoints.
Provides REST API for campaign management.
"""
from typing import List, Optional
from uuid import UUID

from fastapi import APIRouter, HTTPException, Depends, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from ..models import Campaign, CampaignStatus
from ..services import CampaignService, SimulationOrchestrator
from ..database.connection import get_db_session
from ..schemas.campaign import (
    CampaignCreate, CampaignUpdate, CampaignResponse, CampaignListResponse,
    CampaignStartResponse, CampaignStatusResponse
)

router = APIRouter(prefix="/campaigns", tags=["campaigns"])


@router.get("/", response_model=CampaignListResponse)
async def get_campaigns(
    page: int = Query(1, ge=1, description="Page number"),
    limit: int = Query(10, ge=1, le=100, description="Items per page"),
    status: Optional[CampaignStatus] = Query(None, description="Filter by status"),
    persona_id: Optional[UUID] = Query(None, description="Filter by persona ID"),
    sort_by: str = Query("created_at", description="Sort field"),
    sort_order: str = Query("desc", regex="^(asc|desc)$", description="Sort order"),
    db: AsyncSession = Depends(get_db_session)
):
    """Get all campaigns with optional filtering and pagination."""
    service = CampaignService(db)
    
    # Calculate skip
    skip = (page - 1) * limit
    
    # Get campaigns
    campaigns = await service.get_all_campaigns(
        skip=skip,
        limit=limit,
        status_filter=status,
        persona_id_filter=persona_id,
        sort_by=sort_by,
        sort_order=sort_order
    )
    
    # Get total count
    total = await service.get_campaign_count(status_filter=status)
    
    # Convert to response format
    campaign_responses = [CampaignResponse.from_orm(campaign) for campaign in campaigns]
    
    return CampaignListResponse(
        items=campaign_responses,
        page=page,
        limit=limit,
        total=total,
        pages=(total + limit - 1) // limit
    )


@router.get("/{campaign_id}", response_model=CampaignResponse)
async def get_campaign(
    campaign_id: UUID,
    db: AsyncSession = Depends(get_db_session)
):
    """Get campaign by ID."""
    service = CampaignService(db)
    campaign = await service.get_campaign_by_id(campaign_id)
    
    if not campaign:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Campaign not found"
        )
    
    return CampaignResponse.from_orm(campaign)


@router.post("/", response_model=CampaignResponse, status_code=status.HTTP_201_CREATED)
async def create_campaign(
    campaign_data: CampaignCreate,
    db: AsyncSession = Depends(get_db_session)
):
    """Create a new campaign."""
    service = CampaignService(db)
    
    # Validate data
    errors = await service.validate_campaign_data(campaign_data.dict())
    if errors:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail={"validation_errors": errors}
        )
    
    # Create campaign
    try:
        campaign = await service.create_campaign(campaign_data.dict())
        return CampaignResponse.from_orm(campaign)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.put("/{campaign_id}", response_model=CampaignResponse)
async def update_campaign(
    campaign_id: UUID,
    campaign_data: CampaignUpdate,
    db: AsyncSession = Depends(get_db_session)
):
    """Update campaign by ID."""
    service = CampaignService(db)
    
    # Check if campaign exists
    if not await service.campaign_exists(campaign_id):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Campaign not found"
        )
    
    # Prepare update data (exclude None values)
    update_data = {k: v for k, v in campaign_data.dict().items() if v is not None}
    
    if not update_data:
        # No changes to make
        campaign = await service.get_campaign_by_id(campaign_id)
        return CampaignResponse.from_orm(campaign)
    
    # Validate data
    update_data['id'] = str(campaign_id)  # Add ID for validation
    errors = await service.validate_campaign_data(update_data)
    if errors:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail={"validation_errors": errors}
        )
    
    # Update campaign
    try:
        campaign = await service.update_campaign(campaign_id, update_data)
        if not campaign:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Campaign not found"
            )
        
        return CampaignResponse.from_orm(campaign)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.delete("/{campaign_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_campaign(
    campaign_id: UUID,
    db: AsyncSession = Depends(get_db_session)
):
    """Delete campaign by ID."""
    service = CampaignService(db)
    
    # Check if campaign exists
    if not await service.campaign_exists(campaign_id):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Campaign not found"
        )
    
    # Delete campaign
    success = await service.delete_campaign(campaign_id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Campaign not found"
        )


@router.post("/{campaign_id}/start", response_model=CampaignStartResponse)
async def start_campaign(
    campaign_id: UUID,
    db: AsyncSession = Depends(get_db_session)
):
    """Start a campaign simulation."""
    service = CampaignService(db)
    orchestrator = SimulationOrchestrator(db)
    
    # Check if campaign exists
    campaign = await service.get_campaign_by_id(campaign_id)
    if not campaign:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Campaign not found"
        )
    
    # Check if campaign can be started or is already running
    if campaign.status == 'running':
        # Campaign is already running, return current status
        return CampaignStartResponse(
            campaign_id=campaign_id,
            status=campaign.status,
            message="Campaign is already running"
        )
    elif not campaign.can_start():
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"Cannot start campaign in status: {campaign.status}"
        )
    
    # Start campaign
    try:
        started_campaign = await service.start_campaign(campaign_id)
        if not started_campaign:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Failed to start campaign"
            )
        
        # Start simulation
        simulation_started = await orchestrator.start_campaign_simulation(campaign_id)
        if not simulation_started:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Failed to start simulation"
            )
        
        return CampaignStartResponse(
            campaign_id=campaign_id,
            status=started_campaign.status,
            message="Campaign started successfully"
        )
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.post("/{campaign_id}/pause", response_model=CampaignStartResponse)
async def pause_campaign(
    campaign_id: UUID,
    db: AsyncSession = Depends(get_db_session)
):
    """Pause a campaign simulation."""
    service = CampaignService(db)
    orchestrator = SimulationOrchestrator(db)
    
    # Check if campaign exists
    campaign = await service.get_campaign_by_id(campaign_id)
    if not campaign:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Campaign not found"
        )
    
    # Check if campaign can be paused
    if not campaign.can_pause():
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"Cannot pause campaign in status: {campaign.status}"
        )
    
    # Pause campaign
    try:
        paused_campaign = await service.pause_campaign(campaign_id)
        if not paused_campaign:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Failed to pause campaign"
            )
        
        # Pause simulation
        simulation_paused = await orchestrator.pause_campaign_simulation(campaign_id)
        if not simulation_paused:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Failed to pause simulation"
            )
        
        return CampaignStartResponse(
            campaign_id=campaign_id,
            status=paused_campaign.status.value,
            message="Campaign paused successfully"
        )
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.post("/{campaign_id}/resume", response_model=CampaignStartResponse)
async def resume_campaign(
    campaign_id: UUID,
    db: AsyncSession = Depends(get_db_session)
):
    """Resume a campaign simulation."""
    service = CampaignService(db)
    orchestrator = SimulationOrchestrator(db)
    
    # Check if campaign exists
    campaign = await service.get_campaign_by_id(campaign_id)
    if not campaign:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Campaign not found"
        )
    
    # Check if campaign can be resumed
    if not campaign.can_resume():
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"Cannot resume campaign in status: {campaign.status}"
        )
    
    # Resume campaign
    try:
        resumed_campaign = await service.resume_campaign(campaign_id)
        if not resumed_campaign:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Failed to resume campaign"
            )
        
        # Resume simulation
        simulation_resumed = await orchestrator.resume_campaign_simulation(campaign_id)
        if not simulation_resumed:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Failed to resume simulation"
            )
        
        return CampaignStartResponse(
            campaign_id=campaign_id,
            status=resumed_campaign.status.value,
            message="Campaign resumed successfully"
        )
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.get("/{campaign_id}/status", response_model=CampaignStatusResponse)
async def get_campaign_status(
    campaign_id: UUID,
    db: AsyncSession = Depends(get_db_session)
):
    """Get campaign simulation status."""
    orchestrator = SimulationOrchestrator(db)
    
    status_info = await orchestrator.get_campaign_status(campaign_id)
    if not status_info:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Campaign not found"
        )
    
    return CampaignStatusResponse(**status_info)


@router.post("/{campaign_id}/start-real-navigation", response_model=CampaignResponse)
async def start_campaign_real_navigation(
    campaign_id: UUID,
    db: AsyncSession = Depends(get_db_session)
):
    """Start campaign with real navigation to target URL."""
    orchestrator = SimulationOrchestrator(db)
    
    # Vérifier que la campagne existe
    campaign_service = CampaignService(db)
    campaign = await campaign_service.get_campaign_by_id(campaign_id)
    if not campaign:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Campaign not found"
        )
    
    # Vérifier que la campagne a une URL cible
    if not campaign.target_url:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Campaign must have a target URL for real navigation"
        )
    
    # Lancer la campagne avec navigation réelle
    success = await orchestrator.start_campaign_with_real_navigation(campaign_id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to start campaign with real navigation"
        )
    
    # Récupérer la campagne mise à jour
    updated_campaign = await campaign_service.get_campaign_by_id(campaign_id)
    return CampaignResponse.from_orm(updated_campaign)
