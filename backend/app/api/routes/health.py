from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.api.dependencies import get_db, get_rabbitmq_from_request
from app.infrastructure.rabbitmq import RabbitMQConnection
from app.schemas.health import HealthResponse
from app.services.health_checker import (
    DatabaseHealthChecker,
    HealthService,
    RabbitMQHealthChecker,
)

router = APIRouter(tags=["Health"])


def get_health_service(
    db: Session = Depends(get_db),
    rabbitmq: RabbitMQConnection = Depends(get_rabbitmq_from_request),
) -> HealthService:
    """Get health service with all checkers."""
    checkers = [
        DatabaseHealthChecker(db),
        RabbitMQHealthChecker(rabbitmq),
    ]
    return HealthService(checkers)


@router.get("/health", response_model=HealthResponse)
async def health_check(
    health_service: HealthService = Depends(get_health_service),
):
    """Check the health of all services."""
    return await health_service.check_all()
