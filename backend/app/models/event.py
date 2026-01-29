import uuid
from datetime import datetime, timezone

from sqlalchemy import Column, String, DateTime, Index, ForeignKey
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import relationship

from app.db.base import Base


def utc_now() -> datetime:
    return datetime.now(timezone.utc)


class Event(Base):
    __tablename__ = "events"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    source_id = Column(UUID(as_uuid=True), ForeignKey("sources.id"), nullable=False, index=True)
    event_type = Column(String(255), nullable=False)
    data = Column(JSONB, nullable=False, default=dict)
    timestamp = Column(DateTime(timezone=True), nullable=False, index=True)
    created_at = Column(DateTime(timezone=True), default=utc_now)

    # Relationships
    source = relationship("Source")

    __table_args__ = (
        Index("ix_events_source_timestamp", "source_id", "timestamp"),
        # Note: GIN index on 'data' intentionally omitted - high write cost, not currently queried
        # Add it only if you need to filter events by JSON fields: WHERE data->>'field' = 'value'
    )
