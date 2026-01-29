"""Condition type evaluators for rule evaluation."""

from app.models.rule import AlertRule
from app.schemas.evaluation import EvaluationResponse
from app.services.evaluators.base import BaseConditionEvaluator


class CountConditionEvaluator(BaseConditionEvaluator):
    """Evaluator for count-based conditions."""

    def evaluate(self, rule: AlertRule, events: list[dict]) -> EvaluationResponse:
        """Count events matching the condition."""
        matches = sum(
            1
            for event in events
            if self.check_condition(
                event.get("data", {}).get(rule.condition_field),
                rule.condition_operator,
                rule.condition_value,
            )
        )

        triggered = matches >= rule.condition_threshold
        return EvaluationResponse(
            triggered=triggered,
            matches=matches,
            threshold=rule.condition_threshold,
            message=f"Found {matches} matching events (threshold: {rule.condition_threshold})",
        )


class ThresholdConditionEvaluator(BaseConditionEvaluator):
    """Evaluator for threshold-based conditions (all events must match)."""

    def evaluate(self, rule: AlertRule, events: list[dict]) -> EvaluationResponse:
        """Check if ALL events meet the threshold condition."""
        total = 0
        matching = 0

        for event in events:
            field_value = event.get("data", {}).get(rule.condition_field)
            if field_value is not None:
                total += 1
                if self.check_condition(
                    field_value, rule.condition_operator, rule.condition_value
                ):
                    matching += 1

        if total == 0:
            return EvaluationResponse(
                triggered=False,
                matches=0,
                threshold=rule.condition_threshold,
                message="No events with the specified field found",
            )

        has_enough_events = total >= rule.condition_threshold
        all_match = matching == total
        triggered = has_enough_events and all_match

        if not has_enough_events:
            message = f"Only {total} events (need {rule.condition_threshold})"
        elif all_match:
            message = f"All {matching}/{total} events meet condition"
        else:
            message = f"Only {matching}/{total} events meet condition"

        return EvaluationResponse(
            triggered=triggered,
            matches=matching,
            threshold=rule.condition_threshold,
            message=message,
        )
