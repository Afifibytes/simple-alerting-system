from uuid import UUID

from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session

from app.api.dependencies import get_db
from app.repositories.source_repository import SourceRepository
from app.schemas.pagination import PaginatedResponse
from app.schemas.source import SourceCreate, SourceUpdate, SourceResponse
from app.services.source_service import SourceService

router = APIRouter(prefix="/sources", tags=["Sources"])


def get_source_service(db: Session = Depends(get_db)) -> SourceService:
    repository = SourceRepository(db)
    return SourceService(repository)


@router.post("", response_model=SourceResponse, status_code=status.HTTP_201_CREATED)
async def create_source(
    source: SourceCreate,
    service: SourceService = Depends(get_source_service),
):
    """Create a new event source."""
    return service.create(source)


@router.get("", response_model=PaginatedResponse[SourceResponse])
async def list_sources(
    active_only: bool = Query(False, description="Filter to active sources only"),
    search: str | None = Query(None, description="Search by name (case-insensitive)"),
    offset: int = Query(0, ge=0, description="Number of items to skip"),
    limit: int = Query(50, ge=1, le=1000, description="Maximum items to return"),
    service: SourceService = Depends(get_source_service),
):
    """List event sources with pagination and filtering."""
    items, total = service.get_all(
        active_only=active_only, search=search, offset=offset, limit=limit
    )
    return PaginatedResponse(
        items=items,
        total=total,
        offset=offset,
        limit=limit,
        has_more=(offset + len(items)) < total,
    )


@router.get("/{source_id}", response_model=SourceResponse)
async def get_source(
    source_id: UUID,
    service: SourceService = Depends(get_source_service),
):
    """Get a specific source by ID."""
    return service.get_by_id(source_id)


@router.patch("/{source_id}", response_model=SourceResponse)
async def update_source(
    source_id: UUID,
    source_update: SourceUpdate,
    service: SourceService = Depends(get_source_service),
):
    """Update a source."""
    return service.update(source_id, source_update)


@router.delete("/{source_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_source(
    source_id: UUID,
    service: SourceService = Depends(get_source_service),
):
    """Delete a source."""
    service.delete(source_id)
