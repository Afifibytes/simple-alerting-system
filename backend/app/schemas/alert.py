from datetime import datetime
from uuid import UUID

from pydantic import BaseModel

from app.models.alert import AlertStatus


class AlertResponse(BaseModel):
    id: UUID
    rule_id: UUID
    rule_name: str
    status: AlertStatus
    triggered_at: datetime
    acknowledged_at: datetime | None
    resolved_at: datetime | None
    matches_count: int
    severity: str
    message: str | None

    model_config = {"from_attributes": True}


class AlertAcknowledge(BaseModel):
    pass


class AlertResolve(BaseModel):
    message: str | None = None
