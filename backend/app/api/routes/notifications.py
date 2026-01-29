from uuid import UUID

from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session

from app.api.dependencies import get_db
from app.models.notification import ChannelType
from app.repositories.notification_repository import NotificationChannelRepository
from app.schemas.notification import (
    NotificationChannelCreate,
    NotificationChannelUpdate,
    NotificationChannelResponse,
)
from app.schemas.pagination import PaginatedResponse
from app.services.notification_service import NotificationChannelService

router = APIRouter(prefix="/notification-channels", tags=["Notification Channels"])


def get_notification_service(db: Session = Depends(get_db)) -> NotificationChannelService:
    repository = NotificationChannelRepository(db)
    return NotificationChannelService(repository)


@router.post("", response_model=NotificationChannelResponse, status_code=status.HTTP_201_CREATED)
async def create_channel(
    channel: NotificationChannelCreate,
    service: NotificationChannelService = Depends(get_notification_service),
):
    """Create a new notification channel."""
    return service.create(channel)


@router.get("", response_model=PaginatedResponse[NotificationChannelResponse])
async def list_channels(
    active_only: bool = Query(False, description="Filter to active channels only"),
    channel_type: ChannelType | None = Query(None, description="Filter by channel type"),
    offset: int = Query(0, ge=0, description="Number of items to skip"),
    limit: int = Query(50, ge=1, le=1000, description="Maximum items to return"),
    service: NotificationChannelService = Depends(get_notification_service),
):
    """List notification channels with pagination and filtering."""
    items, total = service.get_all(
        active_only=active_only,
        channel_type=channel_type.value if channel_type else None,
        offset=offset,
        limit=limit,
    )
    return PaginatedResponse(
        items=items,
        total=total,
        offset=offset,
        limit=limit,
        has_more=(offset + len(items)) < total,
    )


@router.get("/{channel_id}", response_model=NotificationChannelResponse)
async def get_channel(
    channel_id: UUID,
    service: NotificationChannelService = Depends(get_notification_service),
):
    """Get a specific notification channel by ID."""
    return service.get_by_id(channel_id)


@router.patch("/{channel_id}", response_model=NotificationChannelResponse)
async def update_channel(
    channel_id: UUID,
    channel_update: NotificationChannelUpdate,
    service: NotificationChannelService = Depends(get_notification_service),
):
    """Update a notification channel."""
    return service.update(channel_id, channel_update)


@router.delete("/{channel_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_channel(
    channel_id: UUID,
    service: NotificationChannelService = Depends(get_notification_service),
):
    """Delete a notification channel."""
    service.delete(channel_id)
