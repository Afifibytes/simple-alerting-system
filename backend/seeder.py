#!/usr/bin/env python3
"""Database seeder for the Simple Alerting System."""
import uuid
from datetime import datetime, timezone, timedelta
import random

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.config import settings
from app.models import (
    Source,
    NotificationChannel,
    ChannelType,
    AlertRule,
    ConditionType,
    Severity,
    Alert,
    AlertStatus,
    Event,
)


def utc_now() -> datetime:
    return datetime.now(timezone.utc)


def seed_database():
    """Seed the database with sample data."""
    engine = create_engine(settings.database_url)
    Session = sessionmaker(bind=engine)
    session = Session()

    try:
        # Check if data already exists
        existing_sources = session.query(Source).count()
        if existing_sources > 0:
            print("Database already contains data. Skipping seeding.")
            return

        print("Seeding database...")

        # Create Sources
        sources = [
            Source(
                id=uuid.uuid4(),
                name="web-api-prod",
                description="Production Web API server metrics and events",
                owner="platform-team",
                is_active=True,
            ),
            Source(
                id=uuid.uuid4(),
                name="payment-service",
                description="Payment processing service events",
                owner="payments-team",
                is_active=True,
            ),
            Source(
                id=uuid.uuid4(),
                name="user-auth",
                description="User authentication and authorization service",
                owner="security-team",
                is_active=True,
            ),
            Source(
                id=uuid.uuid4(),
                name="database-monitor",
                description="PostgreSQL database health monitoring",
                owner="dba-team",
                is_active=True,
            ),
            Source(
                id=uuid.uuid4(),
                name="cdn-edge-nodes",
                description="CDN edge node performance metrics",
                owner="infrastructure-team",
                is_active=False,  # Inactive source for testing
            ),
        ]
        session.add_all(sources)
        session.flush()
        print(f"Created {len(sources)} sources")

        # Create Notification Channels
        channels = [
            NotificationChannel(
                id=uuid.uuid4(),
                name="ops-email",
                channel_type=ChannelType.email,
                config={"recipients": ["ops@example.com", "oncall@example.com"]},
                is_active=True,
            ),
            NotificationChannel(
                id=uuid.uuid4(),
                name="critical-slack",
                channel_type=ChannelType.slack,
                config={
                    "webhook_url": "https://hooks.slack.com/services/T00/B00/XXX",
                    "channel": "#critical-alerts",
                },
                is_active=True,
            ),
            NotificationChannel(
                id=uuid.uuid4(),
                name="pagerduty-webhook",
                channel_type=ChannelType.webhook,
                config={
                    "url": "https://events.pagerduty.com/v2/enqueue",
                    "headers": {"Content-Type": "application/json"},
                },
                is_active=True,
            ),
            NotificationChannel(
                id=uuid.uuid4(),
                name="dev-slack",
                channel_type=ChannelType.slack,
                config={
                    "webhook_url": "https://hooks.slack.com/services/T00/B01/YYY",
                    "channel": "#dev-alerts",
                },
                is_active=True,
            ),
            NotificationChannel(
                id=uuid.uuid4(),
                name="security-email",
                channel_type=ChannelType.email,
                config={"recipients": ["security@example.com"]},
                is_active=False,  # Inactive channel for testing
            ),
        ]
        session.add_all(channels)
        session.flush()
        print(f"Created {len(channels)} notification channels")

        # Create Alert Rules
        rules = [
            AlertRule(
                id=uuid.uuid4(),
                name="High Error Rate - Web API",
                source_id=sources[0].id,
                condition_type=ConditionType.count,
                condition_field="error_code",
                condition_operator="==",
                condition_value="500",
                condition_threshold=10,
                severity=Severity.high,
                time_window_seconds=300,
                notification_channels=[channels[0], channels[1], channels[2]],
            ),
            AlertRule(
                id=uuid.uuid4(),
                name="Payment Failures",
                source_id=sources[1].id,
                condition_type=ConditionType.count,
                condition_field="status",
                condition_operator="==",
                condition_value="failed",
                condition_threshold=5,
                severity=Severity.high,
                time_window_seconds=600,
                notification_channels=[channels[1], channels[2]],
            ),
            AlertRule(
                id=uuid.uuid4(),
                name="Failed Login Attempts",
                source_id=sources[2].id,
                condition_type=ConditionType.count,
                condition_field="event_type",
                condition_operator="==",
                condition_value="login_failed",
                condition_threshold=20,
                severity=Severity.medium,
                time_window_seconds=300,
                notification_channels=[channels[0], channels[3]],
            ),
            AlertRule(
                id=uuid.uuid4(),
                name="Database Connection Pool Exhaustion",
                source_id=sources[3].id,
                condition_type=ConditionType.threshold,
                condition_field="active_connections",
                condition_operator=">",
                condition_value="90",
                condition_threshold=3,
                severity=Severity.high,
                time_window_seconds=60,
                notification_channels=[channels[0], channels[1], channels[2]],
            ),
            AlertRule(
                id=uuid.uuid4(),
                name="Slow API Response Time",
                source_id=sources[0].id,
                condition_type=ConditionType.threshold,
                condition_field="response_time_ms",
                condition_operator=">",
                condition_value="2000",
                condition_threshold=5,
                severity=Severity.medium,
                time_window_seconds=300,
                notification_channels=[channels[3]],
            ),
            AlertRule(
                id=uuid.uuid4(),
                name="Low Payment Success Rate",
                source_id=sources[1].id,
                condition_type=ConditionType.threshold,
                condition_field="success_rate",
                condition_operator="<",
                condition_value="95",
                condition_threshold=3,
                severity=Severity.medium,
                time_window_seconds=900,
                notification_channels=[channels[0]],
            ),
        ]
        session.add_all(rules)
        session.flush()
        print(f"Created {len(rules)} alert rules")

        # Create Alerts (some triggered, acknowledged, resolved)
        now = utc_now()
        alerts = [
            Alert(
                id=uuid.uuid4(),
                rule_id=rules[0].id,
                status=AlertStatus.triggered,
                triggered_at=now - timedelta(minutes=15),
                matches_count=12,
                severity="high",
                message="Error rate exceeded threshold: 12 errors in 5 minutes",
            ),
            Alert(
                id=uuid.uuid4(),
                rule_id=rules[1].id,
                status=AlertStatus.acknowledged,
                triggered_at=now - timedelta(hours=2),
                acknowledged_at=now - timedelta(hours=1, minutes=45),
                matches_count=7,
                severity="high",
                message="Payment failures detected: 7 failed transactions",
            ),
            Alert(
                id=uuid.uuid4(),
                rule_id=rules[2].id,
                status=AlertStatus.resolved,
                triggered_at=now - timedelta(days=1),
                acknowledged_at=now - timedelta(days=1) + timedelta(minutes=10),
                resolved_at=now - timedelta(days=1) + timedelta(hours=1),
                matches_count=25,
                severity="medium",
                message="Multiple failed login attempts from IP range 192.168.1.0/24",
            ),
            Alert(
                id=uuid.uuid4(),
                rule_id=rules[3].id,
                status=AlertStatus.triggered,
                triggered_at=now - timedelta(minutes=5),
                matches_count=4,
                severity="high",
                message="Database connection pool at 95% capacity",
            ),
            Alert(
                id=uuid.uuid4(),
                rule_id=rules[4].id,
                status=AlertStatus.resolved,
                triggered_at=now - timedelta(hours=6),
                acknowledged_at=now - timedelta(hours=5, minutes=50),
                resolved_at=now - timedelta(hours=5),
                matches_count=8,
                severity="medium",
                message="API response times exceeded 2000ms threshold",
            ),
        ]
        session.add_all(alerts)
        session.flush()
        print(f"Created {len(alerts)} alerts")

        # Create Events
        event_types = [
            ("web-api-prod", "http_request", lambda: {
                "method": random.choice(["GET", "POST", "PUT", "DELETE"]),
                "path": random.choice(["/api/users", "/api/orders", "/api/products"]),
                "status_code": random.choice([200, 200, 200, 201, 400, 404, 500]),
                "response_time_ms": random.randint(50, 3000),
                "error_code": random.choice([None, None, None, "500", "502"]),
            }),
            ("payment-service", "payment_attempt", lambda: {
                "amount": round(random.uniform(10, 500), 2),
                "currency": "USD",
                "status": random.choice(["success", "success", "success", "failed", "pending"]),
                "payment_method": random.choice(["credit_card", "debit_card", "paypal"]),
            }),
            ("user-auth", "auth_event", lambda: {
                "event_type": random.choice(["login_success", "login_success", "login_failed", "logout"]),
                "user_id": f"user_{random.randint(1000, 9999)}",
                "ip_address": f"192.168.{random.randint(1, 255)}.{random.randint(1, 255)}",
            }),
            ("database-monitor", "db_metrics", lambda: {
                "active_connections": random.randint(20, 100),
                "query_time_avg_ms": random.randint(5, 500),
                "replication_lag_seconds": random.randint(0, 10),
            }),
        ]

        events = []
        for i in range(100):  # Create 100 sample events
            source_name, event_type, data_generator = random.choice(event_types)
            source = next(s for s in sources if s.name == source_name)
            events.append(
                Event(
                    id=uuid.uuid4(),
                    source_id=source.id,
                    event_type=event_type,
                    data=data_generator(),
                    timestamp=now - timedelta(minutes=random.randint(0, 120)),
                )
            )
        session.add_all(events)
        session.flush()
        print(f"Created {len(events)} events")

        session.commit()
        print("\nDatabase seeding completed successfully!")

    except Exception as e:
        session.rollback()
        print(f"Error seeding database: {e}")
        raise
    finally:
        session.close()


if __name__ == "__main__":
    seed_database()