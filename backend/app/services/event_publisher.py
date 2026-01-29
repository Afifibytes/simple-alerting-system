"""Event publisher service for RabbitMQ."""

import json
from datetime import datetime
from typing import Any

import aio_pika

from app.config import settings
from app.schemas.event import EventCreate


class EventPublisher:
    """Publishes events to RabbitMQ. Single responsibility: message publishing."""

    def __init__(self, channel: aio_pika.abc.AbstractChannel):
        self._channel = channel

    async def publish(self, event: EventCreate) -> dict[str, Any]:
        """Publish event to RabbitMQ queue for async processing."""
        timestamp = datetime.utcnow()
        event_data = {
            "timestamp": timestamp.isoformat(),
            "source": event.source,
            "event_type": event.event_type,
            "data": event.data,
        }

        queue = await self._channel.declare_queue(settings.events_queue, durable=True)

        await self._channel.default_exchange.publish(
            aio_pika.Message(
                body=json.dumps(event_data).encode(),
                delivery_mode=aio_pika.DeliveryMode.PERSISTENT,
            ),
            routing_key=queue.name,
        )

        return event_data
