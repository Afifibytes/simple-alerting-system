"""Rule service - business logic layer for alert rules."""

from uuid import UUID

from sqlalchemy.orm import Session

from app.exceptions import EntityNotFoundError
from app.models.rule import AlertRule
from app.repositories.alert_repository import AlertRepository
from app.repositories.notification_repository import NotificationChannelRepository
from app.repositories.rule_repository import RuleRepository
from app.schemas.evaluation import EvaluationResponse
from app.schemas.rule import AlertRuleCreate, AlertRuleUpdate
from app.services.rule_evaluator import RuleEvaluator


class RuleService:
    """Orchestrates rule operations. API layer should only interact with this service."""

    def __init__(
        self,
        db: Session,
        repository: RuleRepository,
        notification_repository: NotificationChannelRepository,
        alert_repository: AlertRepository,
    ):
        self._db = db
        self._repository = repository
        self._evaluator = RuleEvaluator(db)
        self._notification_repository = notification_repository
        self._alert_repository = alert_repository

    def create(self, rule: AlertRuleCreate) -> AlertRule:
        """Create a new alert rule with optional notification channels."""
        notification_channels = None
        if rule.notification_channel_ids:
            notification_channels = self._notification_repository.get_by_ids(
                rule.notification_channel_ids
            )
        return self._repository.create(rule, notification_channels)

    def get_all(
        self,
        source_id: UUID | None = None,
        severity: str | None = None,
        offset: int = 0,
        limit: int = 50,
    ) -> tuple[list[AlertRule], int]:
        """Get alert rules with pagination. Returns (items, total_count)."""
        return self._repository.get_all(
            source_id=source_id, severity=severity, offset=offset, limit=limit
        )

    def get_by_id(self, rule_id: UUID) -> AlertRule:
        """Get a rule by ID. Raises EntityNotFoundError if not found."""
        rule = self._repository.get_by_id(rule_id)
        if rule is None:
            raise EntityNotFoundError("Rule", str(rule_id))
        return rule

    def update(self, rule_id: UUID, rule_update: AlertRuleUpdate) -> AlertRule:
        """Update a rule. Raises EntityNotFoundError if not found."""
        notification_channels = None
        if rule_update.notification_channel_ids is not None:
            notification_channels = self._notification_repository.get_by_ids(
                rule_update.notification_channel_ids
            )

        rule = self._repository.update(rule_id, rule_update, notification_channels)
        if rule is None:
            raise EntityNotFoundError("Rule", str(rule_id))
        return rule

    def delete(self, rule_id: UUID) -> None:
        """Delete a rule. Raises EntityNotFoundError if not found."""
        if not self._repository.delete(rule_id):
            raise EntityNotFoundError("Rule", str(rule_id))

    def evaluate(self, rule_id: UUID, create_alert: bool = True) -> EvaluationResponse:
        """Evaluate a rule against current events. Optionally creates alert if triggered."""
        rule = self.get_by_id(rule_id)
        result = self._evaluator.evaluate(rule)

        if create_alert and result.triggered:
            self._alert_repository.create(
                rule=rule,
                matches_count=result.matches,
                message=result.message,
            )

        return result
