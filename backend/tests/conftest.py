"""Test fixtures and configuration."""

import pytest
from datetime import datetime, timezone
from uuid import uuid4

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.db.base import Base

# Import all models to register them with Base.metadata (required for create_all)
from app.models.source import Source  # noqa: F401
from app.models.rule import AlertRule, ConditionType, Severity  # noqa: F401
from app.models.event import Event  # noqa: F401
from app.models.alert import Alert, AlertStatus  # noqa: F401
from app.models.notification import NotificationChannel, ChannelType  # noqa: F401


@pytest.fixture
def in_memory_db():
    """Create an in-memory SQLite database for testing."""
    engine = create_engine(
        "sqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    Base.metadata.create_all(engine)
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@pytest.fixture
def sample_source(in_memory_db):
    """Create a sample source for testing."""
    source = Source(
        id=uuid4(),
        name="test-source",
        description="Test source",
        is_active=True,
    )
    in_memory_db.add(source)
    in_memory_db.commit()
    in_memory_db.refresh(source)
    return source


@pytest.fixture
def sample_count_rule(in_memory_db, sample_source):
    """Create a sample count-based rule."""
    rule = AlertRule(
        id=uuid4(),
        name="High Error Count",
        source_id=sample_source.id,
        condition_type=ConditionType.count,
        condition_field="level",
        condition_operator="eq",
        condition_value="error",
        condition_threshold=3,
        severity=Severity.high,
        time_window_seconds=300,
    )
    in_memory_db.add(rule)
    in_memory_db.commit()
    in_memory_db.refresh(rule)
    return rule


@pytest.fixture
def sample_threshold_rule(in_memory_db, sample_source):
    """Create a sample threshold-based rule."""
    rule = AlertRule(
        id=uuid4(),
        name="Low Success Rate",
        source_id=sample_source.id,
        condition_type=ConditionType.threshold,
        condition_field="success_rate",
        condition_operator="<",
        condition_value="95",
        condition_threshold=3,
        severity=Severity.medium,
        time_window_seconds=300,
    )
    in_memory_db.add(rule)
    in_memory_db.commit()
    in_memory_db.refresh(rule)
    return rule


@pytest.fixture
def sample_events(in_memory_db, sample_source):
    """Create sample events for testing."""
    now = datetime.now(timezone.utc)
    events = [
        Event(
            id=uuid4(),
            source_id=sample_source.id,
            event_type="log",
            data={"level": "error", "message": "Error 1"},
            timestamp=now,
        ),
        Event(
            id=uuid4(),
            source_id=sample_source.id,
            event_type="log",
            data={"level": "error", "message": "Error 2"},
            timestamp=now,
        ),
        Event(
            id=uuid4(),
            source_id=sample_source.id,
            event_type="log",
            data={"level": "info", "message": "Info message"},
            timestamp=now,
        ),
    ]
    for event in events:
        in_memory_db.add(event)
    in_memory_db.commit()
    return events
