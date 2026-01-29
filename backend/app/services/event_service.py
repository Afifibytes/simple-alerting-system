"""Event service - business logic layer for events."""

from app.schemas.event import EventCreate, EventIngestResponse
from app.services.event_publisher import EventPublisher


class EventService:
    """Orchestrates event operations. API layer should only interact with this service."""

    def __init__(self, publisher: EventPublisher):
        self._publisher = publisher

    async def ingest(self, event: EventCreate) -> EventIngestResponse:
        """Ingest an event for processing."""
        event_data = await self._publisher.publish(event)
        return EventIngestResponse(
            timestamp=event_data["timestamp"],
            source=event_data["source"],
            event_type=event_data["event_type"],
            data=event_data["data"],
        )
