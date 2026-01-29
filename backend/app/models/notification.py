import enum
import uuid
from datetime import datetime, timezone

from sqlalchemy import Column, String, DateTime, Boolean, Enum, ForeignKey, Index, Table
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import relationship

from app.db.base import Base


def utc_now() -> datetime:
    return datetime.now(timezone.utc)


class ChannelType(str, enum.Enum):
    email = "email"
    webhook = "webhook"
    slack = "slack"


# Many-to-many junction table
rule_notification_channels = Table(
    "rule_notification_channels",
    Base.metadata,
    Column("rule_id", UUID(as_uuid=True), ForeignKey("alert_rules.id"), primary_key=True),
    Column("channel_id", UUID(as_uuid=True), ForeignKey("notification_channels.id"), primary_key=True),
)


class NotificationChannel(Base):
    __tablename__ = "notification_channels"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(255), nullable=False, unique=True)
    channel_type = Column(Enum(ChannelType), nullable=False)
    config = Column(JSONB, nullable=False)  # Stores type-specific config (email addresses, webhook URLs, etc.)
    is_active = Column(Boolean, default=True, nullable=False)
    created_at = Column(DateTime(timezone=True), default=utc_now)
    updated_at = Column(DateTime(timezone=True), default=utc_now, onupdate=utc_now)

    # Relationships
    rules = relationship(
        "AlertRule",
        secondary=rule_notification_channels,
        back_populates="notification_channels",
    )

    __table_args__ = (
        Index("ix_notification_channels_type", "channel_type"),
        Index("ix_notification_channels_is_active", "is_active"),
    )
