"""Comparison operators for rule evaluation."""

from typing import Any

from app.services.operators.base import BaseOperator


class ContainsOperator(BaseOperator):
    """Check if value contains the condition value (case-insensitive)."""

    def evaluate(self, value: Any, condition_value: str) -> bool:
        return condition_value.lower() in str(value).lower()


class EqualsOperator(BaseOperator):
    """Check if value equals the condition value."""

    def evaluate(self, value: Any, condition_value: str) -> bool:
        return str(value) == condition_value


class NumericOperator(BaseOperator):
    """Base class for numeric comparison operators."""

    def _to_numeric(self, value: Any, condition_value: str) -> tuple[float, float] | None:
        """Convert values to numeric, returns None if conversion fails."""
        try:
            return float(value), float(condition_value)
        except (ValueError, TypeError):
            return None

    def evaluate(self, value: Any, condition_value: str) -> bool:
        result = self._to_numeric(value, condition_value)
        if result is None:
            return False
        return self._compare(result[0], result[1])

    def _compare(self, a: float, b: float) -> bool:
        raise NotImplementedError


class GreaterThanOperator(NumericOperator):
    """Check if value is greater than condition value."""

    def _compare(self, a: float, b: float) -> bool:
        return a > b


class LessThanOperator(NumericOperator):
    """Check if value is less than condition value."""

    def _compare(self, a: float, b: float) -> bool:
        return a < b


class GreaterThanOrEqualOperator(NumericOperator):
    """Check if value is greater than or equal to condition value."""

    def _compare(self, a: float, b: float) -> bool:
        return a >= b


class LessThanOrEqualOperator(NumericOperator):
    """Check if value is less than or equal to condition value."""

    def _compare(self, a: float, b: float) -> bool:
        return a <= b
