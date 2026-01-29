from uuid import UUID

from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session

from app.api.dependencies import get_db, get_rabbitmq_from_request
from app.infrastructure.rabbitmq import RabbitMQConnection
from app.repositories.event_repository import EventRepository
from app.schemas.event import EventCreate, EventResponse, EventIngestResponse
from app.schemas.pagination import PaginatedResponse
from app.services.event_publisher import EventPublisher
from app.services.event_service import EventService

router = APIRouter(prefix="/events", tags=["Events"])


def get_event_service(
    rabbitmq: RabbitMQConnection = Depends(get_rabbitmq_from_request),
) -> EventService:
    """Build event service with its dependencies."""
    publisher = EventPublisher(rabbitmq.get_channel())
    return EventService(publisher)


def get_event_repository(db: Session = Depends(get_db)) -> EventRepository:
    """Get event repository."""
    return EventRepository(db)


@router.get("", response_model=PaginatedResponse[EventResponse])
async def list_events(
    source_id: UUID | None = Query(None, description="Filter by source ID"),
    event_type: str | None = Query(None, description="Filter by event type"),
    offset: int = Query(0, ge=0, description="Number of items to skip"),
    limit: int = Query(50, ge=1, le=1000, description="Maximum items to return"),
    repository: EventRepository = Depends(get_event_repository),
):
    """List events with pagination and filtering."""
    events, total = repository.get_all(
        source_id=source_id, event_type=event_type, offset=offset, limit=limit
    )

    # Transform to response with source_name
    items = [
        EventResponse(
            id=event.id,
            source_id=event.source_id,
            source_name=event.source.name if event.source else "Unknown",
            event_type=event.event_type,
            data=event.data,
            timestamp=event.timestamp,
        )
        for event in events
    ]

    return PaginatedResponse(
        items=items,
        total=total,
        offset=offset,
        limit=limit,
        has_more=(offset + len(items)) < total,
    )


@router.post("", response_model=EventIngestResponse, status_code=status.HTTP_202_ACCEPTED)
async def ingest_event(
    event: EventCreate,
    service: EventService = Depends(get_event_service),
):
    """
    Ingest an event for processing.

    Events are published to a message queue and processed asynchronously.
    """
    return await service.ingest(event)
