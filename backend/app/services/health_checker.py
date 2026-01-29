"""Health check services."""

import logging
from abc import ABC, abstractmethod

from sqlalchemy import text
from sqlalchemy.orm import Session

from app.infrastructure.rabbitmq import RabbitMQConnection

logger = logging.getLogger(__name__)


class BaseHealthChecker(ABC):
    """Abstract base class for health checkers."""

    @abstractmethod
    async def check(self) -> tuple[str, str]:
        """Check health. Returns (name, status)."""
        pass


class DatabaseHealthChecker(BaseHealthChecker):
    """Checks database connectivity."""

    def __init__(self, db: Session):
        self._db = db

    async def check(self) -> tuple[str, str]:
        try:
            self._db.execute(text("SELECT 1"))
            return ("database", "connected")
        except Exception as e:
            logger.error("Database health check failed: %s", e)
            return ("database", "disconnected")


class RabbitMQHealthChecker(BaseHealthChecker):
    """Checks RabbitMQ connectivity."""

    def __init__(self, rabbitmq: RabbitMQConnection):
        self._rabbitmq = rabbitmq

    async def check(self) -> tuple[str, str]:
        try:
            channel = self._rabbitmq.get_channel()
            if channel is None:
                return ("rabbitmq", "disconnected")
            return ("rabbitmq", "connected")
        except Exception as e:
            logger.error("RabbitMQ health check failed: %s", e)
            return ("rabbitmq", "disconnected")


class HealthService:
    """Aggregates all health checks."""

    def __init__(self, checkers: list[BaseHealthChecker]):
        self._checkers = checkers

    async def check_all(self) -> dict[str, str]:
        """Run all health checks and return results."""
        results = {"status": "healthy"}

        for checker in self._checkers:
            name, status = await checker.check()
            results[name] = status
            if status != "connected":
                results["status"] = "unhealthy"

        return results
