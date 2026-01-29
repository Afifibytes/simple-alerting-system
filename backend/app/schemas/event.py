import json
from datetime import datetime
from typing import Any
from uuid import UUID

from pydantic import BaseModel, Field, field_validator

# Maximum size for event data (64KB)
MAX_EVENT_DATA_SIZE = 65536
MAX_EVENT_DATA_KEYS = 100
MAX_NESTING_DEPTH = 10


def _check_depth(obj: Any, current_depth: int = 0) -> int:
    """Check nesting depth of an object."""
    if current_depth > MAX_NESTING_DEPTH:
        return current_depth
    if isinstance(obj, dict):
        if not obj:
            return current_depth
        return max(_check_depth(v, current_depth + 1) for v in obj.values())
    elif isinstance(obj, list):
        if not obj:
            return current_depth
        return max(_check_depth(v, current_depth + 1) for v in obj)
    return current_depth


class EventCreate(BaseModel):
    source: str = Field(..., min_length=1, max_length=255)
    event_type: str = Field(..., min_length=1, max_length=255)
    data: dict[str, Any] = Field(default_factory=dict)

    @field_validator("data")
    @classmethod
    def validate_data_size(cls, v: dict[str, Any]) -> dict[str, Any]:
        """Validate event data size and structure."""
        # Check number of top-level keys
        if len(v) > MAX_EVENT_DATA_KEYS:
            raise ValueError(f"Event data exceeds maximum of {MAX_EVENT_DATA_KEYS} keys")

        # Check serialized size
        serialized = json.dumps(v)
        if len(serialized) > MAX_EVENT_DATA_SIZE:
            raise ValueError(f"Event data exceeds maximum size of {MAX_EVENT_DATA_SIZE} bytes")

        # Check nesting depth
        depth = _check_depth(v)
        if depth > MAX_NESTING_DEPTH:
            raise ValueError(f"Event data exceeds maximum nesting depth of {MAX_NESTING_DEPTH}")

        return v


class EventResponse(BaseModel):
    id: UUID
    source_id: UUID
    source_name: str
    event_type: str
    data: dict[str, Any]
    timestamp: datetime

    model_config = {"from_attributes": True}


class EventIngestResponse(BaseModel):
    """Response for event ingestion (before DB persistence)."""
    timestamp: datetime
    source: str
    event_type: str
    data: dict[str, Any]
