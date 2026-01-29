"""Repository for event data access."""

from datetime import datetime, timezone
from uuid import UUID

from sqlalchemy.orm import Session, Query, joinedload
from sqlalchemy.exc import SQLAlchemyError

from app.exceptions import DatabaseError
from app.models.event import Event
from app.models.source import Source


class EventRepository:
    def __init__(self, db: Session):
        self._db = db

    def _calculate_window_bounds(self, window_seconds: int) -> tuple[datetime, datetime]:
        """Calculate start and end times for a time window."""
        now = datetime.now(timezone.utc)
        window_start = datetime.fromtimestamp(
            now.timestamp() - window_seconds, tz=timezone.utc
        )
        return window_start, now

    def _apply_time_window_filter(self, query: Query, window_seconds: int, limit: int | None = None) -> Query:
        """Apply time window filter to a query with optional limit for OOM protection."""
        window_start, now = self._calculate_window_bounds(window_seconds)
        filtered = (
            query
            .filter(Event.timestamp >= window_start)
            .filter(Event.timestamp <= now)
            .order_by(Event.timestamp.desc())
        )
        if limit is not None:
            filtered = filtered.limit(limit)
        return filtered

    def get_all(
        self,
        source_id: UUID | None = None,
        event_type: str | None = None,
        offset: int = 0,
        limit: int = 50,
    ) -> tuple[list[type[Event]], int]:
        """Get paginated events with optional filters. Uses eager loading to prevent N+1."""
        try:
            # Base query for counting (without eager loading for efficiency)
            count_query = self._db.query(Event)
            if source_id:
                count_query = count_query.filter(Event.source_id == source_id)
            if event_type:
                count_query = count_query.filter(Event.event_type == event_type)
            total = count_query.count()

            # Query with eager loading for source relationship
            query = self._db.query(Event).options(joinedload(Event.source))
            if source_id:
                query = query.filter(Event.source_id == source_id)
            if event_type:
                query = query.filter(Event.event_type == event_type)

            items = (
                query.order_by(Event.timestamp.desc())
                .offset(offset)
                .limit(limit)
                .all()
            )
            return items, total
        except SQLAlchemyError as e:
            raise DatabaseError(f"Failed to fetch events: {e}") from e

    def create(
        self,
        source_name: str,
        event_type: str,
        data: dict,
        timestamp: datetime,
    ) -> Event:
        """Create a new event. Looks up source by name."""
        try:
            # Find source by name
            source = self._db.query(Source).filter(Source.name == source_name).first()
            if source is None:
                # Auto-create source if it doesn't exist
                source = Source(name=source_name)
                self._db.add(source)
                self._db.flush()

            event = Event(
                source_id=source.id,
                event_type=event_type,
                data=data,
                timestamp=timestamp,
            )
            self._db.add(event)
            self._db.commit()
            self._db.refresh(event)
            return event
        except SQLAlchemyError as e:
            self._db.rollback()
            raise DatabaseError(f"Failed to create event: {e}") from e

    def get_by_source_in_window(
        self,
        source_name: str,
        window_seconds: int,
        limit: int | None = None,
    ) -> list[Event]:
        """Get events for a source within a time window.

        Args:
            source_name: Name of the event source
            window_seconds: Time window in seconds
            limit: Optional max events to return (OOM protection)
        """
        try:
            query = (
                self._db.query(Event)
                .join(Source)
                .filter(Source.name == source_name)
            )
            return self._apply_time_window_filter(query, window_seconds, limit).all()
        except SQLAlchemyError as e:
            raise DatabaseError(f"Failed to fetch events: {e}") from e

    def get_by_source_id_in_window(
        self,
        source_id: UUID,
        window_seconds: int,
        limit: int | None = None,
    ) -> list[Event]:
        """Get events for a source ID within a time window.

        Args:
            source_id: UUID of the event source
            window_seconds: Time window in seconds
            limit: Optional max events to return (OOM protection)
        """
        try:
            query = self._db.query(Event).filter(Event.source_id == source_id)
            return self._apply_time_window_filter(query, window_seconds, limit).all()
        except SQLAlchemyError as e:
            raise DatabaseError(f"Failed to fetch events: {e}") from e

    def create_batch(
        self,
        events: list[dict],
    ) -> int:
        """Create multiple events in a single transaction. Returns count created.

        Each event dict should have: source_name, event_type, data, timestamp
        """
        if not events:
            return 0

        try:
            # Group events by source name to minimize source lookups
            source_cache: dict[str, Source] = {}
            event_objects = []

            for event_data in events:
                source_name = event_data["source_name"]

                # Cache source lookups
                if source_name not in source_cache:
                    source = self._db.query(Source).filter(Source.name == source_name).first()
                    if source is None:
                        source = Source(name=source_name)
                        self._db.add(source)
                        self._db.flush()
                    source_cache[source_name] = source

                event = Event(
                    source_id=source_cache[source_name].id,
                    event_type=event_data["event_type"],
                    data=event_data["data"],
                    timestamp=event_data["timestamp"],
                )
                event_objects.append(event)

            self._db.add_all(event_objects)
            self._db.commit()
            return len(event_objects)
        except SQLAlchemyError as e:
            self._db.rollback()
            raise DatabaseError(f"Failed to create event batch: {e}") from e

    def delete_old_events(self, older_than_seconds: int) -> int:
        """Delete events older than specified seconds. Returns count deleted."""
        try:
            cutoff, _ = self._calculate_window_bounds(older_than_seconds)
            result = (
                self._db.query(Event)
                .filter(Event.timestamp < cutoff)
                .delete(synchronize_session=False)
            )
            self._db.commit()
            return result
        except SQLAlchemyError as e:
            self._db.rollback()
            raise DatabaseError(f"Failed to delete old events: {e}") from e
