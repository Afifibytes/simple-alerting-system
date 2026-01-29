"""Rule evaluation service."""

from sqlalchemy.orm import Session

from app.config import settings
from app.models.rule import AlertRule
from app.repositories.event_repository import EventRepository
from app.schemas.evaluation import EvaluationResponse
from app.services.evaluators import evaluator_registry


class RuleEvaluator:
    """Evaluates rules against events from the database."""

    def __init__(self, db: Session):
        self._db = db
        self._evaluator_registry = evaluator_registry

    def _get_events(self, source_name: str, window_seconds: int) -> list[dict]:
        """Get events from database (source of truth).

        Note: We always query the database to ensure complete data.
        The cache is not used here because it may have incomplete data
        (e.g., after worker restart, or if TTL expired some events).
        """
        repo = EventRepository(self._db)
        db_events = repo.get_by_source_in_window(
            source_name, window_seconds, limit=settings.max_events_per_evaluation
        )

        return [
            {
                "timestamp": event.timestamp.isoformat(),
                "source": source_name,
                "event_type": event.event_type,
                "data": event.data,
            }
            for event in db_events
        ]

    def evaluate(self, rule: AlertRule) -> EvaluationResponse:
        """Evaluate a rule against stored events."""
        source_name = rule.source_rel.name if rule.source_rel else None
        if not source_name:
            return EvaluationResponse(
                triggered=False,
                matches=0,
                threshold=rule.condition_threshold,
                message="Rule has no associated source",
            )

        events = self._get_events(source_name, rule.time_window_seconds)

        if not events:
            return EvaluationResponse(
                triggered=False,
                matches=0,
                threshold=rule.condition_threshold,
                message="No events found in time window",
            )

        evaluator = self._evaluator_registry.get(rule.condition_type.value)
        if evaluator is None:
            return EvaluationResponse(
                triggered=False,
                matches=0,
                threshold=rule.condition_threshold,
                message="Unknown condition type",
            )

        return evaluator.evaluate(rule, events)
