"""Tests for condition evaluators - core business logic."""

import pytest
from unittest.mock import MagicMock

from app.models.rule import AlertRule
from app.services.evaluators.conditions import (
    CountConditionEvaluator,
    ThresholdConditionEvaluator,
)


class TestCountConditionEvaluator:
    """Tests for count-based condition evaluation."""

    def setup_method(self):
        self.evaluator = CountConditionEvaluator()

    def _make_rule(self, threshold: int = 3) -> AlertRule:
        """Create a mock rule for testing."""
        rule = MagicMock(spec=AlertRule)
        rule.condition_threshold = threshold
        return rule

    def test_triggers_when_matches_meet_threshold(self):
        """Should trigger when matching events >= threshold."""
        rule = self._make_rule(threshold=3)

        result = self.evaluator.evaluate(rule, matching_count=3, total_with_field=3)

        assert result.triggered is True
        assert result.matches == 3
        assert result.threshold == 3

    def test_triggers_when_matches_exceed_threshold(self):
        """Should trigger when matching events > threshold."""
        rule = self._make_rule(threshold=3)

        result = self.evaluator.evaluate(rule, matching_count=5, total_with_field=5)

        assert result.triggered is True
        assert result.matches == 5
        assert result.threshold == 3

    def test_does_not_trigger_below_threshold(self):
        """Should not trigger when matching events < threshold."""
        rule = self._make_rule(threshold=3)

        result = self.evaluator.evaluate(rule, matching_count=2, total_with_field=3)

        assert result.triggered is False
        assert result.matches == 2
        assert result.threshold == 3

    def test_handles_zero_matches(self):
        """Should not trigger with no matching events."""
        rule = self._make_rule(threshold=1)

        result = self.evaluator.evaluate(rule, matching_count=0, total_with_field=5)

        assert result.triggered is False
        assert result.matches == 0

    def test_handles_zero_events(self):
        """Should not trigger with no events at all."""
        rule = self._make_rule(threshold=1)

        result = self.evaluator.evaluate(rule, matching_count=0, total_with_field=0)

        assert result.triggered is False
        assert result.matches == 0


class TestThresholdConditionEvaluator:
    """Tests for threshold-based condition evaluation (all events must match)."""

    def setup_method(self):
        self.evaluator = ThresholdConditionEvaluator()

    def _make_rule(self, threshold: int = 3) -> AlertRule:
        """Create a mock rule for testing."""
        rule = MagicMock(spec=AlertRule)
        rule.condition_threshold = threshold
        return rule

    def test_triggers_when_all_match_and_enough_events(self):
        """Should trigger when all events match AND total >= threshold."""
        rule = self._make_rule(threshold=3)

        result = self.evaluator.evaluate(rule, matching_count=3, total_with_field=3)

        assert result.triggered is True
        assert result.matches == 3

    def test_triggers_when_all_match_and_more_than_threshold(self):
        """Should trigger when all events match AND total > threshold."""
        rule = self._make_rule(threshold=3)

        result = self.evaluator.evaluate(rule, matching_count=5, total_with_field=5)

        assert result.triggered is True
        assert result.matches == 5

    def test_does_not_trigger_when_not_all_match(self):
        """Should not trigger when some events don't match."""
        rule = self._make_rule(threshold=3)

        result = self.evaluator.evaluate(rule, matching_count=2, total_with_field=3)

        assert result.triggered is False
        assert result.matches == 2
        assert "Only 2/3 events" in result.message

    def test_does_not_trigger_below_threshold_count(self):
        """Should not trigger when total events < threshold, even if all match."""
        rule = self._make_rule(threshold=5)

        result = self.evaluator.evaluate(rule, matching_count=3, total_with_field=3)

        assert result.triggered is False
        assert "Only 3 events" in result.message

    def test_handles_zero_events(self):
        """Should not trigger with no events."""
        rule = self._make_rule(threshold=1)

        result = self.evaluator.evaluate(rule, matching_count=0, total_with_field=0)

        assert result.triggered is False
        assert "No events with the specified field" in result.message

    def test_threshold_of_one_with_single_matching_event(self):
        """Edge case: threshold=1 with one matching event."""
        rule = self._make_rule(threshold=1)

        result = self.evaluator.evaluate(rule, matching_count=1, total_with_field=1)

        assert result.triggered is True
        assert result.matches == 1
