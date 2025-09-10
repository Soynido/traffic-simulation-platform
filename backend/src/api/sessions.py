"""
Sessions API endpoints.
Provides REST API for session management.
"""
from typing import List, Optional
from uuid import UUID

from fastapi import APIRouter, HTTPException, Depends, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from ..models import Session, SessionStatus
from ..services import SessionService
from ..database.connection import get_db_session
from ..schemas.session import SessionResponse, SessionListResponse

router = APIRouter(prefix="/sessions", tags=["sessions"])


@router.get("/", response_model=SessionListResponse)
async def get_sessions(
    page: int = Query(1, ge=1, description="Page number"),
    limit: int = Query(10, ge=1, le=100, description="Items per page"),
    status: Optional[SessionStatus] = Query(None, description="Filter by status"),
    campaign_id: Optional[UUID] = Query(None, description="Filter by campaign ID"),
    sort_by: str = Query("created_at", description="Sort field"),
    sort_order: str = Query("desc", regex="^(asc|desc)$", description="Sort order"),
    db: AsyncSession = Depends(get_db_session)
):
    """Get all sessions with optional filtering and pagination."""
    service = SessionService(db)
    
    # Calculate skip
    skip = (page - 1) * limit
    
    # Get sessions
    sessions = await service.get_all_sessions(
        skip=skip,
        limit=limit,
        status_filter=status,
        campaign_id_filter=campaign_id
    )
    
    # Get total count
    total = await service.get_session_count(
        campaign_id=campaign_id,
        status_filter=status
    )
    
    # Convert to response format
    session_responses = [SessionResponse.from_orm(session) for session in sessions]
    
    return SessionListResponse(
        items=session_responses,
        page=page,
        limit=limit,
        total=total,
        pages=(total + limit - 1) // limit
    )


@router.get("/{session_id}", response_model=SessionResponse)
async def get_session(
    session_id: UUID,
    include: Optional[str] = Query(None, description="Include related data (page_visits, actions)"),
    db: AsyncSession = Depends(get_db_session)
):
    """Get session by ID."""
    service = SessionService(db)
    session = await service.get_session_by_id(session_id)
    
    if not session:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Session not found"
        )
    
    return SessionResponse.from_orm(session)


@router.get("/campaign/{campaign_id}", response_model=SessionListResponse)
async def get_sessions_by_campaign(
    campaign_id: UUID,
    page: int = Query(1, ge=1, description="Page number"),
    limit: int = Query(10, ge=1, le=100, description="Items per page"),
    status: Optional[SessionStatus] = Query(None, description="Filter by status"),
    db: AsyncSession = Depends(get_db_session)
):
    """Get sessions by campaign ID."""
    service = SessionService(db)
    
    # Calculate skip
    skip = (page - 1) * limit
    
    # Get sessions
    sessions = await service.get_sessions_by_campaign(
        campaign_id=campaign_id,
        skip=skip,
        limit=limit,
        status_filter=status
    )
    
    # Get total count
    total = await service.get_session_count(
        campaign_id=campaign_id,
        status_filter=status
    )
    
    # Convert to response format
    session_responses = [SessionResponse.from_orm(session) for session in sessions]
    
    return SessionListResponse(
        items=session_responses,
        page=page,
        limit=limit,
        total=total,
        pages=(total + limit - 1) // limit
    )


@router.get("/persona/{persona_id}", response_model=SessionListResponse)
async def get_sessions_by_persona(
    persona_id: UUID,
    page: int = Query(1, ge=1, description="Page number"),
    limit: int = Query(10, ge=1, le=100, description="Items per page"),
    db: AsyncSession = Depends(get_db_session)
):
    """Get sessions by persona ID."""
    service = SessionService(db)
    
    # Calculate skip
    skip = (page - 1) * limit
    
    # Get sessions
    sessions = await service.get_sessions_by_persona(
        persona_id=persona_id,
        skip=skip,
        limit=limit
    )
    
    # Get total count
    total = await service.get_session_count()
    
    # Convert to response format
    session_responses = [SessionResponse.from_orm(session) for session in sessions]
    
    return SessionListResponse(
        items=session_responses,
        page=page,
        limit=limit,
        total=total,
        pages=(total + limit - 1) // limit
    )


@router.post("/{session_id}/start", response_model=SessionResponse)
async def start_session(
    session_id: UUID,
    db: AsyncSession = Depends(get_db_session)
):
    """Start a session."""
    service = SessionService(db)
    
    # Check if session exists
    session = await service.get_session_by_id(session_id)
    if not session:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Session not found"
        )
    
    # Check if session can be started
    if not session.can_start():
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"Cannot start session in status: {session.status}"
        )
    
    # Start session
    try:
        started_session = await service.start_session(session_id)
        if not started_session:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Failed to start session"
            )
        
        return SessionResponse.from_orm(started_session)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.post("/{session_id}/complete", response_model=SessionResponse)
async def complete_session(
    session_id: UUID,
    duration_ms: Optional[int] = Query(None, description="Session duration in milliseconds"),
    db: AsyncSession = Depends(get_db_session)
):
    """Complete a session."""
    service = SessionService(db)
    
    # Check if session exists
    session = await service.get_session_by_id(session_id)
    if not session:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Session not found"
        )
    
    # Check if session can be completed
    if not session.can_complete():
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"Cannot complete session in status: {session.status}"
        )
    
    # Complete session
    try:
        completed_session = await service.complete_session(session_id, duration_ms)
        if not completed_session:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Failed to complete session"
            )
        
        return SessionResponse.from_orm(completed_session)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.post("/{session_id}/fail", response_model=SessionResponse)
async def fail_session(
    session_id: UUID,
    error_message: Optional[str] = Query(None, description="Error message"),
    db: AsyncSession = Depends(get_db_session)
):
    """Mark session as failed."""
    service = SessionService(db)
    
    # Check if session exists
    session = await service.get_session_by_id(session_id)
    if not session:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Session not found"
        )
    
    # Check if session can be failed
    if not session.can_fail():
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"Cannot fail session in status: {session.status}"
        )
    
    # Fail session
    try:
        failed_session = await service.fail_session(session_id, error_message)
        if not failed_session:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Failed to fail session"
            )
        
        return SessionResponse.from_orm(failed_session)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.post("/{session_id}/timeout", response_model=SessionResponse)
async def timeout_session(
    session_id: UUID,
    db: AsyncSession = Depends(get_db_session)
):
    """Mark session as timed out."""
    service = SessionService(db)
    
    # Check if session exists
    session = await service.get_session_by_id(session_id)
    if not session:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Session not found"
        )
    
    # Check if session can be timed out
    if not session.can_fail():
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"Cannot timeout session in status: {session.status}"
        )
    
    # Timeout session
    try:
        timed_out_session = await service.timeout_session(session_id)
        if not timed_out_session:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Failed to timeout session"
            )
        
        return SessionResponse.from_orm(timed_out_session)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.put("/{session_id}/metrics", response_model=SessionResponse)
async def update_session_metrics(
    session_id: UUID,
    pages_visited: Optional[int] = Query(None, ge=0, description="Number of pages visited"),
    total_actions: Optional[int] = Query(None, ge=0, description="Total number of actions"),
    db: AsyncSession = Depends(get_db_session)
):
    """Update session metrics."""
    service = SessionService(db)
    
    # Check if session exists
    if not await service.session_exists(session_id):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Session not found"
        )
    
    # Update metrics
    try:
        updated_session = await service.update_session_metrics(
            session_id=session_id,
            pages_visited=pages_visited,
            total_actions=total_actions
        )
        
        if not updated_session:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Session not found"
            )
        
        return SessionResponse.from_orm(updated_session)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
