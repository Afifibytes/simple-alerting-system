"""Source service - business logic layer for sources."""

from uuid import UUID

from app.exceptions import EntityNotFoundError
from app.models.source import Source
from app.repositories.source_repository import SourceRepository
from app.schemas.source import SourceCreate, SourceUpdate


class SourceService:
    def __init__(self, repository: SourceRepository):
        self._repository = repository

    def create(self, source: SourceCreate) -> Source:
        return self._repository.create(source)

    def get_all(
        self,
        active_only: bool = False,
        search: str | None = None,
        offset: int = 0,
        limit: int = 50,
    ) -> tuple[list[Source], int]:
        """Get sources with pagination. Returns (items, total_count)."""
        return self._repository.get_all(
            active_only=active_only, search=search, offset=offset, limit=limit
        )

    def get_by_id(self, source_id: UUID) -> Source:
        source = self._repository.get_by_id(source_id)
        if source is None:
            raise EntityNotFoundError("Source", str(source_id))
        return source

    def get_by_name(self, name: str) -> Source:
        source = self._repository.get_by_name(name)
        if source is None:
            raise EntityNotFoundError("Source", name)
        return source

    def update(self, source_id: UUID, source_update: SourceUpdate) -> Source:
        return self._repository.update(source_id, source_update)

    def delete(self, source_id: UUID) -> None:
        if not self._repository.delete(source_id):
            raise EntityNotFoundError("Source", str(source_id))
