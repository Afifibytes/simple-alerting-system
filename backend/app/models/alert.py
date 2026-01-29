import enum
import uuid
from datetime import datetime, timezone

from sqlalchemy import Column, String, Integer, DateTime, Enum, ForeignKey, Text, Index
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from app.db.base import Base


def utc_now() -> datetime:
    return datetime.now(timezone.utc)


class AlertStatus(str, enum.Enum):
    triggered = "triggered"
    acknowledged = "acknowledged"
    resolved = "resolved"


class Alert(Base):
    __tablename__ = "alerts"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    rule_id = Column(UUID(as_uuid=True), ForeignKey("alert_rules.id"), nullable=False, index=True)
    status = Column(Enum(AlertStatus), default=AlertStatus.triggered, nullable=False)
    triggered_at = Column(DateTime(timezone=True), default=utc_now, nullable=False)
    acknowledged_at = Column(DateTime(timezone=True), nullable=True)
    resolved_at = Column(DateTime(timezone=True), nullable=True)
    matches_count = Column(Integer, nullable=False)
    severity = Column(String(20), nullable=False)
    message = Column(Text, nullable=True)

    # Relationships
    rule = relationship("AlertRule", back_populates="alerts")

    __table_args__ = (
        Index("ix_alerts_status", "status"),
        Index("ix_alerts_severity", "severity"),
        Index("ix_alerts_triggered_at", "triggered_at"),
        # Composite indexes for common query patterns at scale
        Index("ix_alerts_status_triggered_at", "status", "triggered_at"),
        Index("ix_alerts_rule_id_status", "rule_id", "status"),
    )
