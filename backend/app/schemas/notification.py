from datetime import datetime
from typing import Any
from uuid import UUID

from pydantic import BaseModel, Field

from app.models.notification import ChannelType


class NotificationChannelCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=255)
    channel_type: ChannelType
    config: dict[str, Any] = Field(
        ...,
        description="Type-specific configuration. Email: {recipients: [...]}, Webhook: {url: ...}, Slack: {webhook_url: ...}",
    )


class NotificationChannelUpdate(BaseModel):
    name: str | None = Field(None, min_length=1, max_length=255)
    config: dict[str, Any] | None = None
    is_active: bool | None = None


class NotificationChannelResponse(BaseModel):
    id: UUID
    name: str
    channel_type: ChannelType
    config: dict[str, Any]
    is_active: bool
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}
