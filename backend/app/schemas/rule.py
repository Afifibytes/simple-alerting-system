from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, Field

from app.models.notification import ChannelType
from app.models.rule import ConditionType, Severity


class NotificationChannelSummary(BaseModel):
    """Minimal channel info for embedding in rule responses."""
    id: UUID
    name: str
    channel_type: ChannelType

    model_config = {"from_attributes": True}


class AlertRuleCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=255)
    source_id: UUID
    condition_type: ConditionType
    condition_field: str = Field(..., min_length=1, max_length=255)
    condition_operator: str = Field(..., pattern="^(contains|eq|gt|lt|gte|lte)$")
    condition_value: str
    condition_threshold: int = Field(..., ge=1)
    severity: Severity
    time_window_seconds: int = Field(..., ge=1, le=86400)
    notification_channel_ids: list[UUID] = Field(default_factory=list)


class AlertRuleUpdate(BaseModel):
    name: str | None = Field(None, min_length=1, max_length=255)
    condition_type: ConditionType | None = None
    condition_field: str | None = Field(None, min_length=1, max_length=255)
    condition_operator: str | None = Field(None, pattern="^(contains|eq|gt|lt|gte|lte)$")
    condition_value: str | None = None
    condition_threshold: int | None = Field(None, ge=1)
    severity: Severity | None = None
    time_window_seconds: int | None = Field(None, ge=1, le=86400)
    notification_channel_ids: list[UUID] | None = None


class AlertRuleResponse(BaseModel):
    id: UUID
    name: str
    source_id: UUID
    condition_type: ConditionType
    condition_field: str
    condition_operator: str
    condition_value: str
    condition_threshold: int
    severity: Severity
    time_window_seconds: int
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class AlertRuleDetailResponse(AlertRuleResponse):
    """Response with expanded relationships."""
    source_name: str | None = None
    notification_channels: list[NotificationChannelSummary] = Field(default_factory=list)
