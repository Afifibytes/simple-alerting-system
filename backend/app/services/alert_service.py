"""Alert service - business logic layer for alerts."""

from uuid import UUID

from app.exceptions import EntityNotFoundError
from app.models.alert import Alert, AlertStatus
from app.models.rule import AlertRule
from app.repositories.alert_repository import AlertRepository


class AlertService:
    def __init__(self, repository: AlertRepository):
        self._repository = repository

    def create(self, rule: AlertRule, matches_count: int, message: str | None = None) -> Alert:
        return self._repository.create(rule, matches_count, message)

    def get_all(
        self,
        rule_id: UUID | None = None,
        status: AlertStatus | None = None,
        severity: str | None = None,
        offset: int = 0,
        limit: int = 50,
    ) -> tuple[list[type[Alert]], int]:
        """Get alerts with pagination. Returns (items, total_count)."""
        return self._repository.get_all(
            rule_id=rule_id, status=status, severity=severity, offset=offset, limit=limit
        )

    def get_by_id(self, alert_id: UUID) -> Alert:
        alert = self._repository.get_by_id(alert_id)
        if alert is None:
            raise EntityNotFoundError("Alert", str(alert_id))
        return alert

    def acknowledge(self, alert_id: UUID) -> Alert:
        alert = self._repository.acknowledge(alert_id)
        if alert is None:
            raise EntityNotFoundError("Alert", str(alert_id))
        return alert

    def resolve(self, alert_id: UUID, message: str | None = None) -> Alert:
        alert = self._repository.resolve(alert_id, message)
        if alert is None:
            raise EntityNotFoundError("Alert", str(alert_id))
        return alert
