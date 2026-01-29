import asyncio
from uuid import UUID

import pika
from fastapi import APIRouter, Depends, Query, Request
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session

from app.api.dependencies import get_db
from app.config import settings
from app.models.alert import AlertStatus
from app.repositories.alert_repository import AlertRepository
from app.schemas.alert import AlertResponse, AlertResolve
from app.schemas.pagination import PaginatedResponse
from app.services.alert_service import AlertService

router = APIRouter(prefix="/alerts", tags=["Alerts"])

ALERTS_NOTIFICATIONS_EXCHANGE = "alert_notifications"


def get_alert_service(db: Session = Depends(get_db)) -> AlertService:
    repository = AlertRepository(db)
    return AlertService(repository)


def _to_alert_response(alert) -> AlertResponse:
    """Convert Alert model to AlertResponse with rule_name."""
    return AlertResponse(
        id=alert.id,
        rule_id=alert.rule_id,
        rule_name=alert.rule.name if alert.rule else "Unknown",
        status=alert.status,
        triggered_at=alert.triggered_at,
        acknowledged_at=alert.acknowledged_at,
        resolved_at=alert.resolved_at,
        matches_count=alert.matches_count,
        severity=alert.severity,
        message=alert.message,
    )


@router.get("", response_model=PaginatedResponse[AlertResponse])
async def list_alerts(
    rule_id: UUID | None = Query(None, description="Filter by rule ID"),
    status: AlertStatus | None = Query(None, description="Filter by status"),
    severity: str | None = Query(None, description="Filter by severity (low, medium, high)"),
    offset: int = Query(0, ge=0, description="Number of items to skip"),
    limit: int = Query(50, ge=1, le=1000, description="Maximum items to return"),
    service: AlertService = Depends(get_alert_service),
):
    """List alerts with pagination and filtering."""
    items, total = service.get_all(
        rule_id=rule_id, status=status, severity=severity, offset=offset, limit=limit
    )
    return PaginatedResponse(
        items=[_to_alert_response(alert) for alert in items],
        total=total,
        offset=offset,
        limit=limit,
        has_more=(offset + len(items)) < total,
    )


@router.get("/stream")
async def stream_alerts(request: Request):
    """
    SSE endpoint for real-time alert notifications.
    Clients receive a message whenever a new alert is created.
    Uses RabbitMQ fanout exchange for pub/sub.
    """
    async def event_generator():
        connection = None
        channel = None
        queue_name = None

        def setup_rabbitmq():
            """Setup RabbitMQ connection with exclusive queue bound to fanout exchange."""
            nonlocal connection, channel, queue_name
            connection = pika.BlockingConnection(
                pika.URLParameters(settings.rabbitmq_url)
            )
            channel = connection.channel()
            # Declare the fanout exchange (idempotent)
            channel.exchange_declare(
                exchange=ALERTS_NOTIFICATIONS_EXCHANGE,
                exchange_type="fanout",
                durable=False,
            )
            # Create exclusive, auto-delete queue for this SSE client
            result = channel.queue_declare(queue="", exclusive=True)
            queue_name = result.method.queue
            # Bind to fanout exchange
            channel.queue_bind(exchange=ALERTS_NOTIFICATIONS_EXCHANGE, queue=queue_name)
            return channel, queue_name

        def get_message():
            """Non-blocking check for message."""
            method, properties, body = channel.basic_get(queue=queue_name, auto_ack=True)
            if body:
                return body.decode()
            return None

        def cleanup():
            """Close RabbitMQ connection."""
            nonlocal connection
            if connection and not connection.is_closed:
                try:
                    connection.close()
                except Exception:
                    pass

        try:
            # Setup in thread pool (blocking operation)
            await asyncio.to_thread(setup_rabbitmq)
            yield "data: connected\n\n"

            while True:
                if await request.is_disconnected():
                    break

                # Check for message in thread pool
                message = await asyncio.to_thread(get_message)
                if message:
                    yield f"data: {message}\n\n"

                await asyncio.sleep(0.1)
        finally:
            await asyncio.to_thread(cleanup)

    return StreamingResponse(
        event_generator(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no",
        },
    )


@router.get("/{alert_id}", response_model=AlertResponse)
async def get_alert(
    alert_id: UUID,
    service: AlertService = Depends(get_alert_service),
):
    """Get a specific alert by ID."""
    return _to_alert_response(service.get_by_id(alert_id))


@router.post("/{alert_id}/acknowledge", response_model=AlertResponse)
async def acknowledge_alert(
    alert_id: UUID,
    service: AlertService = Depends(get_alert_service),
):
    """Acknowledge an alert."""
    return _to_alert_response(service.acknowledge(alert_id))


@router.post("/{alert_id}/resolve", response_model=AlertResponse)
async def resolve_alert(
    alert_id: UUID,
    body: AlertResolve,
    service: AlertService = Depends(get_alert_service),
):
    """Resolve an alert."""
    return _to_alert_response(service.resolve(alert_id, body.message))
