"""
Event Cleanup Job

Removes old events from the database to prevent unbounded growth.
Run periodically via cron or scheduler.
"""

import sys

from app.config import settings
from app.db.session import SessionLocal
from app.repositories.event_repository import EventRepository

# Force unbuffered output
sys.stdout.reconfigure(line_buffering=True)

# Default retention: 7 days (configurable via EVENT_RETENTION_SECONDS env var)
DEFAULT_RETENTION_SECONDS = 7 * 24 * 60 * 60  # 7 days


def cleanup_old_events(retention_seconds: int | None = None) -> int:
    """Delete events older than retention period. Returns count deleted."""
    retention = retention_seconds or getattr(
        settings, "event_retention_seconds", DEFAULT_RETENTION_SECONDS
    )

    db = SessionLocal()
    try:
        repo = EventRepository(db)
        count = repo.delete_old_events(retention)
        print(f"Deleted {count} events older than {retention // 3600} hours")
        return count
    finally:
        db.close()


def main():
    print("Starting event cleanup...")
    cleanup_old_events()
    print("Cleanup complete")


if __name__ == "__main__":
    main()
