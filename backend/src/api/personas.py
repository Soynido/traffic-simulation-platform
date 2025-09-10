"""
Personas API endpoints.
Provides REST API for persona management.
"""
from typing import List, Optional
from uuid import UUID

from fastapi import APIRouter, HTTPException, Depends, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from ..models import Persona
from ..services import PersonaService
from ..database.connection import get_db_session
from ..schemas.persona import PersonaCreate, PersonaUpdate, PersonaResponse, PersonaListResponse

router = APIRouter(prefix="/personas", tags=["personas"])


@router.get("/", response_model=PersonaListResponse)
async def get_personas(
    page: int = Query(1, ge=1, description="Page number"),
    limit: int = Query(10, ge=1, le=100, description="Items per page"),
    name: Optional[str] = Query(None, description="Filter by name"),
    sort_by: str = Query("name", description="Sort field"),
    sort_order: str = Query("asc", regex="^(asc|desc)$", description="Sort order"),
    db: AsyncSession = Depends(get_db_session)
):
    """Get all personas with optional filtering and pagination."""
    service = PersonaService(db)
    
    # Calculate skip
    skip = (page - 1) * limit
    
    # Get personas
    personas = await service.get_all_personas(
        skip=skip,
        limit=limit,
        name_filter=name,
        sort_by=sort_by,
        sort_order=sort_order
    )
    
    # Get total count
    total = await service.get_persona_count()
    
    # Convert to response format
    persona_responses = [PersonaResponse.from_orm(persona) for persona in personas]
    
    return PersonaListResponse(
        items=persona_responses,
        page=page,
        limit=limit,
        total=total,
        pages=(total + limit - 1) // limit
    )


@router.get("/{persona_id}", response_model=PersonaResponse)
async def get_persona(
    persona_id: UUID,
    db: AsyncSession = Depends(get_db_session)
):
    """Get persona by ID."""
    service = PersonaService(db)
    persona = await service.get_persona_by_id(persona_id)
    
    if not persona:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Persona not found"
        )
    
    return PersonaResponse.from_orm(persona)


@router.post("/", response_model=PersonaResponse, status_code=status.HTTP_201_CREATED)
async def create_persona(
    persona_data: PersonaCreate,
    db: AsyncSession = Depends(get_db_session)
):
    """Create a new persona."""
    service = PersonaService(db)
    
    # Validate data
    errors = await service.validate_persona_data(persona_data.dict())
    if errors:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail={"validation_errors": errors}
        )
    
    # Create persona
    try:
        persona = await service.create_persona(persona_data.dict())
        return PersonaResponse.from_orm(persona)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.put("/{persona_id}", response_model=PersonaResponse)
async def update_persona(
    persona_id: UUID,
    persona_data: PersonaUpdate,
    db: AsyncSession = Depends(get_db_session)
):
    """Update persona by ID."""
    service = PersonaService(db)
    
    # Check if persona exists
    if not await service.persona_exists(persona_id):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Persona not found"
        )
    
    # Prepare update data (exclude None values)
    update_data = {k: v for k, v in persona_data.dict().items() if v is not None}
    
    if not update_data:
        # No changes to make
        persona = await service.get_persona_by_id(persona_id)
        return PersonaResponse.from_orm(persona)
    
    # Validate data
    update_data['id'] = str(persona_id)  # Add ID for validation
    errors = await service.validate_persona_data(update_data)
    if errors:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail={"validation_errors": errors}
        )
    
    # Update persona
    try:
        persona = await service.update_persona(persona_id, update_data)
        if not persona:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Persona not found"
            )
        
        return PersonaResponse.from_orm(persona)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.delete("/{persona_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_persona(
    persona_id: UUID,
    db: AsyncSession = Depends(get_db_session)
):
    """Delete persona by ID."""
    service = PersonaService(db)
    
    # Check if persona exists
    if not await service.persona_exists(persona_id):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Persona not found"
        )
    
    # Delete persona
    success = await service.delete_persona(persona_id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Persona not found"
        )
