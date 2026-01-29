"""Base classes for condition evaluators."""

from abc import ABC, abstractmethod

from app.models.rule import AlertRule
from app.schemas.evaluation import EvaluationResponse
from app.services.operators import operator_registry


class BaseConditionEvaluator(ABC):
    """Abstract base class for condition evaluators."""

    def __init__(self):
        self._operator_registry = operator_registry

    def check_condition(
        self, value, operator: str, condition_value: str
    ) -> bool:
        """Check if a value matches the condition using the operator registry."""
        return self._operator_registry.evaluate(operator, value, condition_value)

    @abstractmethod
    def evaluate(self, rule: AlertRule, events: list[dict]) -> EvaluationResponse:
        """Evaluate the condition against events."""
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
