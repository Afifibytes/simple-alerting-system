"""Notification service - business logic layer for notification channels."""

from uuid import UUID

from app.exceptions import EntityNotFoundError
from app.models.notification import NotificationChannel
from app.repositories.notification_repository import NotificationChannelRepository
from app.schemas.notification import NotificationChannelCreate, NotificationChannelUpdate


class NotificationChannelService:
    def __init__(self, repository: NotificationChannelRepository):
        self._repository = repository

    def create(self, channel: NotificationChannelCreate) -> NotificationChannel:
        return self._repository.create(channel)

    def get_all(
        self,
        active_only: bool = False,
        channel_type: str | None = None,
        offset: int = 0,
        limit: int = 50,
    ) -> tuple[list[NotificationChannel], int]:
        """Get channels with pagination. Returns (items, total_count)."""
        return self._repository.get_all(
            active_only=active_only, channel_type=channel_type, offset=offset, limit=limit
        )

    def get_by_id(self, channel_id: UUID) -> NotificationChannel:
        channel = self._repository.get_by_id(channel_id)
        if channel is None:
            raise EntityNotFoundError("NotificationChannel", str(channel_id))
        return channel

    def get_by_ids(self, channel_ids: list[UUID]) -> list[NotificationChannel]:
        return self._repository.get_by_ids(channel_ids)

    def update(self, channel_id: UUID, channel_update: NotificationChannelUpdate) -> NotificationChannel:
        channel = self._repository.update(channel_id, channel_update)
        if channel is None:
            raise EntityNotFoundError("NotificationChannel", str(channel_id))
        return channel

    def delete(self, channel_id: UUID) -> None:
        if not self._repository.delete(channel_id):
            raise EntityNotFoundError("NotificationChannel", str(channel_id))
