"""Tests for condition evaluators - core business logic."""

import pytest
from unittest.mock import MagicMock
from uuid import uuid4

from app.models.rule import AlertRule, ConditionType, Severity
from app.services.evaluators.conditions import (
    CountConditionEvaluator,
    ThresholdConditionEvaluator,
)


class TestCountConditionEvaluator:
    """Tests for count-based condition evaluation."""

    def setup_method(self):
        self.evaluator = CountConditionEvaluator()

    def _make_rule(
        self,
        field: str = "level",
        operator: str = "eq",
        value: str = "error",
        threshold: int = 3,
    ) -> AlertRule:
        """Create a mock rule for testing."""
        rule = MagicMock(spec=AlertRule)
        rule.condition_field = field
        rule.condition_operator = operator
        rule.condition_value = value
        rule.condition_threshold = threshold
        return rule

    def test_triggers_when_matches_meet_threshold(self):
        """Should trigger when matching events >= threshold."""
        rule = self._make_rule(threshold=3)
        events = [
            {"data": {"level": "error"}},
            {"data": {"level": "error"}},
            {"data": {"level": "error"}},
        ]

        result = self.evaluator.evaluate(rule, events)

        assert result.triggered is True
        assert result.matches == 3
        assert result.threshold == 3

    def test_does_not_trigger_below_threshold(self):
        """Should not trigger when matching events < threshold."""
        rule = self._make_rule(threshold=3)
        events = [
            {"data": {"level": "error"}},
            {"data": {"level": "error"}},
            {"data": {"level": "info"}},
        ]

        result = self.evaluator.evaluate(rule, events)

        assert result.triggered is False
        assert result.matches == 2
        assert result.threshold == 3

    def test_handles_empty_events(self):
        """Should not trigger with no events."""
        rule = self._make_rule(threshold=1)
        events = []

        result = self.evaluator.evaluate(rule, events)

        assert result.triggered is False
        assert result.matches == 0

    def test_handles_missing_field(self):
        """Should not count events missing the condition field."""
        rule = self._make_rule(field="missing_field", threshold=1)
        events = [
            {"data": {"level": "error"}},
            {"data": {"other": "value"}},
        ]

        result = self.evaluator.evaluate(rule, events)

        assert result.triggered is False
        assert result.matches == 0

    def test_greater_than_operator(self):
        """Should work with numeric greater than comparisons."""
        rule = self._make_rule(field="count", operator=">", value="10", threshold=2)
        events = [
            {"data": {"count": 15}},
            {"data": {"count": 5}},
            {"data": {"count": 20}},
        ]

        result = self.evaluator.evaluate(rule, events)

        assert result.triggered is True
        assert result.matches == 2

    def test_less_than_operator(self):
        """Should work with numeric less than comparisons."""
        rule = self._make_rule(field="success_rate", operator="<", value="95", threshold=2)
        events = [
            {"data": {"success_rate": 90}},
            {"data": {"success_rate": 98}},
            {"data": {"success_rate": 80}},
        ]

        result = self.evaluator.evaluate(rule, events)

        assert result.triggered is True
        assert result.matches == 2

    def test_contains_operator(self):
        """Should work with string contains check."""
        rule = self._make_rule(field="message", operator="contains", value="timeout", threshold=2)
        events = [
            {"data": {"message": "Connection timeout error"}},
            {"data": {"message": "Success"}},
            {"data": {"message": "Request timeout"}},
        ]

        result = self.evaluator.evaluate(rule, events)

        assert result.triggered is True
        assert result.matches == 2


class TestThresholdConditionEvaluator:
    """Tests for threshold-based condition evaluation (all events must match)."""

    def setup_method(self):
        self.evaluator = ThresholdConditionEvaluator()

    def _make_rule(
        self,
        field: str = "success_rate",
        operator: str = "<",
        value: str = "95",
        threshold: int = 3,
    ) -> AlertRule:
        """Create a mock rule for testing."""
        rule = MagicMock(spec=AlertRule)
        rule.condition_field = field
        rule.condition_operator = operator
        rule.condition_value = value
        rule.condition_threshold = threshold
        return rule

    def test_triggers_when_all_match_and_enough_events(self):
        """Should trigger when all events match AND total >= threshold."""
        rule = self._make_rule(threshold=3)
        events = [
            {"data": {"success_rate": 90}},
            {"data": {"success_rate": 85}},
            {"data": {"success_rate": 92}},
        ]

        result = self.evaluator.evaluate(rule, events)

        assert result.triggered is True
        assert result.matches == 3

    def test_does_not_trigger_when_not_all_match(self):
        """Should not trigger when some events don't match."""
        rule = self._make_rule(threshold=3)
        events = [
            {"data": {"success_rate": 90}},
            {"data": {"success_rate": 98}},  # Does not match < 95
            {"data": {"success_rate": 92}},
        ]

        result = self.evaluator.evaluate(rule, events)

        assert result.triggered is False
        assert result.matches == 2

    def test_does_not_trigger_below_threshold_count(self):
        """Should not trigger when total events < threshold, even if all match."""
        rule = self._make_rule(threshold=5)
        events = [
            {"data": {"success_rate": 90}},
            {"data": {"success_rate": 85}},
            {"data": {"success_rate": 92}},
        ]

        result = self.evaluator.evaluate(rule, events)

        assert result.triggered is False
        assert "Only 3 events" in result.message

    def test_handles_empty_events(self):
        """Should not trigger with no events."""
        rule = self._make_rule(threshold=1)
        events = []

        result = self.evaluator.evaluate(rule, events)

        assert result.triggered is False

    def test_handles_events_without_field(self):
        """Should skip events missing the condition field."""
        rule = self._make_rule(threshold=2)
        events = [
            {"data": {"success_rate": 90}},
            {"data": {"other_field": 100}},  # Missing field, skipped
            {"data": {"success_rate": 85}},
        ]

        result = self.evaluator.evaluate(rule, events)

        assert result.triggered is True
        assert result.matches == 2

    def test_threshold_of_one_with_single_matching_event(self):
        """Edge case: threshold=1 with one matching event."""
        rule = self._make_rule(threshold=1)
        events = [{"data": {"success_rate": 90}}]

        result = self.evaluator.evaluate(rule, events)

        assert result.triggered is True
        assert result.matches == 1
