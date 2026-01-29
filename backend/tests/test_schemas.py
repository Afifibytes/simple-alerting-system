"""Tests for schema validation - security focused."""

import pytest
from pydantic import ValidationError

from app.schemas.event import EventCreate, MAX_EVENT_DATA_SIZE, MAX_EVENT_DATA_KEYS, MAX_NESTING_DEPTH


class TestEventCreateValidation:
    """Tests for event data validation (security)."""

    def test_valid_event_data(self):
        """Should accept valid event data."""
        event = EventCreate(
            source="test-source",
            event_type="log",
            data={"level": "error", "message": "Test error"},
        )
        assert event.source == "test-source"
        assert event.data["level"] == "error"

    def test_empty_data_is_valid(self):
        """Should accept empty data dict."""
        event = EventCreate(
            source="test-source",
            event_type="log",
            data={},
        )
        assert event.data == {}

    def test_rejects_oversized_data(self):
        """Should reject data exceeding size limit."""
        large_value = "x" * (MAX_EVENT_DATA_SIZE + 1)
        with pytest.raises(ValidationError) as exc_info:
            EventCreate(
                source="test-source",
                event_type="log",
                data={"large": large_value},
            )
        assert "maximum size" in str(exc_info.value).lower()

    def test_rejects_too_many_keys(self):
        """Should reject data with too many top-level keys."""
        too_many_keys = {f"key_{i}": i for i in range(MAX_EVENT_DATA_KEYS + 1)}
        with pytest.raises(ValidationError) as exc_info:
            EventCreate(
                source="test-source",
                event_type="log",
                data=too_many_keys,
            )
        assert "keys" in str(exc_info.value).lower()

    def test_rejects_deep_nesting(self):
        """Should reject data with too deep nesting."""
        # Build deeply nested structure
        nested = {"value": "deep"}
        for _ in range(MAX_NESTING_DEPTH + 2):
            nested = {"nested": nested}

        with pytest.raises(ValidationError) as exc_info:
            EventCreate(
                source="test-source",
                event_type="log",
                data=nested,
            )
        assert "depth" in str(exc_info.value).lower()

    def test_accepts_max_allowed_nesting(self):
        """Should accept data at exactly max nesting depth."""
        nested = {"value": "ok"}
        for _ in range(MAX_NESTING_DEPTH - 1):
            nested = {"nested": nested}

        event = EventCreate(
            source="test-source",
            event_type="log",
            data=nested,
        )
        assert event.data is not None

    def test_accepts_max_allowed_keys(self):
        """Should accept data with exactly max keys."""
        max_keys = {f"key_{i}": i for i in range(MAX_EVENT_DATA_KEYS)}
        event = EventCreate(
            source="test-source",
            event_type="log",
            data=max_keys,
        )
        assert len(event.data) == MAX_EVENT_DATA_KEYS

    def test_rejects_empty_source(self):
        """Should reject empty source."""
        with pytest.raises(ValidationError):
            EventCreate(
                source="",
                event_type="log",
                data={},
            )

    def test_rejects_too_long_source(self):
        """Should reject source exceeding max length."""
        with pytest.raises(ValidationError):
            EventCreate(
                source="x" * 256,
                event_type="log",
                data={},
            )

    def test_accepts_nested_arrays(self):
        """Should accept nested arrays within limits."""
        event = EventCreate(
            source="test-source",
            event_type="log",
            data={
                "items": [
                    {"name": "item1", "values": [1, 2, 3]},
                    {"name": "item2", "values": [4, 5, 6]},
                ]
            },
        )
        assert len(event.data["items"]) == 2
