"""Rule evaluation service."""

from sqlalchemy.orm import Session

from app.models.rule import AlertRule
from app.repositories.event_repository import EventRepository
from app.schemas.evaluation import EvaluationResponse
from app.services.evaluators import evaluator_registry


class RuleEvaluator:
    """Evaluates rules against events using database aggregation.

    This pushes COUNT operations to the database instead of loading
    events into memory, providing O(1) memory usage regardless of
    event volume.
    """

    def __init__(self, db: Session):
        self._db = db
        self._repo = EventRepository(db)
        self._evaluator_registry = evaluator_registry

    def evaluate(self, rule: AlertRule) -> EvaluationResponse:
        """Evaluate a rule using database-aggregated counts."""
        source_name = rule.source_rel.name if rule.source_rel else None
        if not source_name:
            return EvaluationResponse(
                triggered=False,
                matches=0,
                threshold=rule.condition_threshold,
                message="Rule has no associated source",
            )

        # Get counts from database (O(1) memory)
        matching_count, total_with_field = self._repo.count_matching_events(
            source_name=source_name,
            window_seconds=rule.time_window_seconds,
            field=rule.condition_field,
            operator=rule.condition_operator,
            value=rule.condition_value,
        )

        if total_with_field == 0:
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

        return evaluator.evaluate(rule, matching_count, total_with_field)
