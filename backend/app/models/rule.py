import enum
import uuid
from datetime import datetime, timezone

from sqlalchemy import Column, String, Integer, DateTime, Enum, Index, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship

from app.db.base import Base
from app.models.notification import rule_notification_channels


class ConditionType(str, enum.Enum):
    count = "count"
    threshold = "threshold"


class Severity(str, enum.Enum):
    low = "low"
    medium = "medium"
    high = "high"


def utc_now() -> datetime:
    return datetime.now(timezone.utc)


class AlertRule(Base):
    __tablename__ = "alert_rules"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(255), nullable=False)
    source_id = Column(UUID(as_uuid=True), ForeignKey("sources.id"), nullable=False, index=True)
    condition_type = Column(Enum(ConditionType), nullable=False)
    condition_field = Column(String(255), nullable=False)
    condition_operator = Column(String(10), nullable=False)
    condition_value = Column(String(255), nullable=False)
    condition_threshold = Column(Integer, nullable=False)
    severity = Column(Enum(Severity), nullable=False)
    time_window_seconds = Column(Integer, nullable=False)
    created_at = Column(DateTime(timezone=True), default=utc_now)
    updated_at = Column(DateTime(timezone=True), default=utc_now, onupdate=utc_now)

    # Relationships
    source_rel = relationship("Source", back_populates="rules")
    alerts = relationship("Alert", back_populates="rule", cascade="all, delete-orphan")
    notification_channels = relationship(
        "NotificationChannel",
        secondary=rule_notification_channels,
        back_populates="rules",
    )

    __table_args__ = (
        Index("ix_alert_rules_source_severity", "source_id", "severity"),
    )
