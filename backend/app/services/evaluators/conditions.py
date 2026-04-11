"""Condition type evaluators for rule evaluation."""

from app.models.rule import AlertRule
from app.schemas.evaluation import EvaluationResponse
from app.services.evaluators.base import BaseConditionEvaluator


class CountConditionEvaluator(BaseConditionEvaluator):
    """Evaluator for count-based conditions.

    Triggers when the number of matching events meets or exceeds the threshold.
    """

    def evaluate(
        self, rule: AlertRule, matching_count: int, total_with_field: int
    ) -> EvaluationResponse:
        """Check if matching event count meets the threshold."""
        triggered = matching_count >= rule.condition_threshold
        return EvaluationResponse(
            triggered=triggered,
            matches=matching_count,
            threshold=rule.condition_threshold,
            message=f"Found {matching_count} matching events (threshold: {rule.condition_threshold})",
        )


class ThresholdConditionEvaluator(BaseConditionEvaluator):
    """Evaluator for threshold-based conditions (all events must match).

    Triggers when:
    1. There are at least threshold number of events with the field
    2. ALL of those events match the condition
    """

    def evaluate(
        self, rule: AlertRule, matching_count: int, total_with_field: int
    ) -> EvaluationResponse:
        """Check if ALL events meet the threshold condition."""
        if total_with_field == 0:
            return EvaluationResponse(
                triggered=False,
                matches=0,
                threshold=rule.condition_threshold,
                message="No events with the specified field found",
            )

        has_enough_events = total_with_field >= rule.condition_threshold
        all_match = matching_count == total_with_field
        triggered = has_enough_events and all_match

        if not has_enough_events:
            message = f"Only {total_with_field} events (need {rule.condition_threshold})"
        elif all_match:
            message = f"All {matching_count}/{total_with_field} events meet condition"
        else:
            message = f"Only {matching_count}/{total_with_field} events meet condition"

        return EvaluationResponse(
            triggered=triggered,
            matches=matching_count,
            threshold=rule.condition_threshold,
            message=message,
        )

class AverageConditionEvaluator(BaseConditionEvaluator):
    """Evaluator for average-based conditions."""
    def evaluate(
        self, rule: AlertRule, matching_count: int, total_with_field: int
    ) -> EvaluationResponse:
        """Check if the average of matching events meets the threshold."""
        if total_with_field == 0:
            return EvaluationResponse(
                triggered=False,
                matches=0,
                threshold=rule.condition_threshold,
                message="No events with the specified field found",
            )

        average = matching_count / total_with_field
        triggered = average >= rule.condition_threshold

        return EvaluationResponse(
            triggered=triggered,
            matches=matching_count,
            threshold=rule.condition_threshold,
            message=f"Average of {average} (threshold: {rule.condition_threshold})",
        )