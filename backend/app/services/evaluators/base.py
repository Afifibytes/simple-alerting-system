"""Base classes for condition evaluators."""

from abc import ABC, abstractmethod

from app.models.rule import AlertRule
from app.schemas.evaluation import EvaluationResponse


class BaseConditionEvaluator(ABC):
    """Abstract base class for condition evaluators."""

    @abstractmethod
    def evaluate(
        self, rule: AlertRule, matching_count: int, total_with_field: int
    ) -> EvaluationResponse:
        """Evaluate the condition using pre-computed counts from the database.

        Args:
            rule: The alert rule being evaluated
            matching_count: Number of events matching the condition
            total_with_field: Total number of events that have the specified field
        """
        pass


class EvaluatorRegistry:
    """Registry for condition evaluators. Allows extension without modification (OCP)."""

    def __init__(self):
        self._evaluators: dict[str, BaseConditionEvaluator] = {}

    def register(self, condition_type: str, evaluator: BaseConditionEvaluator) -> None:
        """Register an evaluator."""
        self._evaluators[condition_type] = evaluator

    def get(self, condition_type: str) -> BaseConditionEvaluator | None:
        """Get an evaluator by condition type."""
        return self._evaluators.get(condition_type)
