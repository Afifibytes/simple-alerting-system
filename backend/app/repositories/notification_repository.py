"""Repository for notification channel data access."""
from uuid import UUID

from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError

from app.exceptions import DatabaseError
from app.models.notification import NotificationChannel
from app.repositories.base import BaseRepository
from app.schemas.notification import NotificationChannelCreate


class NotificationChannelRepository(BaseRepository[NotificationChannel]):
    def __init__(self, db: Session):
        super().__init__(db, NotificationChannel)

    def create(self, channel: NotificationChannelCreate, **kwargs) -> NotificationChannel:
        try:
            return super().create(channel)
        except DatabaseError as e:
            if "UNIQUE" in str(e) or "duplicate" in str(e).lower():
                raise DatabaseError(f"Channel with name '{channel.name}' already exists") from e
            raise

    def get_all(
        self,
        active_only: bool = False,
        channel_type: str | None = None,
        offset: int = 0,
        limit: int = 50,
    ) -> tuple[list[NotificationChannel], int]:
        query = self._db.query(NotificationChannel)
        if active_only:
            query = query.filter(NotificationChannel.is_active == True)
        if channel_type:
            query = query.filter(NotificationChannel.channel_type == channel_type)
        return self.get_all_paginated(query, NotificationChannel.name, offset, limit)

    def get_by_ids(self, channel_ids: list[UUID]) -> list[type[NotificationChannel]]:
        try:
            return self._db.query(NotificationChannel).filter(NotificationChannel.id.in_(channel_ids)).all()
        except SQLAlchemyError as e:
            raise DatabaseError(f"Failed to fetch notification channels: {e}") from e
