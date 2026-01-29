"""Base classes for condition operators."""

from abc import ABC, abstractmethod
from typing import Any


class BaseOperator(ABC):
    """Abstract base class for condition operators."""

    @abstractmethod
    def evaluate(self, value: Any, condition_value: str) -> bool:
        """Evaluate if value matches the condition."""
        pass


class OperatorRegistry:
    """Registry for condition operators. Allows extension without modification (OCP)."""

    def __init__(self):
        self._operators: dict[str, BaseOperator] = {}

    def register(self, name: str, operator: BaseOperator) -> None:
        """Register an operator."""
        self._operators[name] = operator

    def get(self, name: str) -> BaseOperator | None:
        """Get an operator by name."""
        return self._operators.get(name)

    def evaluate(self, operator_name: str, value: Any, condition_value: str) -> bool:
        """Evaluate using the specified operator."""
        if value is None:
            return False
        operator = self.get(operator_name)
        if operator is None:
            return False
        return operator.evaluate(value, condition_value)
