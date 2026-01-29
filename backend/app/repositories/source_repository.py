"""Repository for source data access."""

from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError

from app.exceptions import DatabaseError
from app.models.source import Source
from app.repositories.base import BaseRepository
from app.schemas.source import SourceCreate


class SourceRepository(BaseRepository[Source]):
    def __init__(self, db: Session):
        super().__init__(db, Source)

    def create(self, source: SourceCreate, **kwargs) -> Source:
        try:
            return super().create(source)
        except DatabaseError as e:
            if "UNIQUE" in str(e) or "duplicate" in str(e).lower():
                raise DatabaseError(f"Source with name '{source.name}' already exists") from e
            raise

    def get_all(
        self,
        active_only: bool = False,
        search: str | None = None,
        offset: int = 0,
        limit: int = 50,
    ) -> tuple[list[Source], int]:
        query = self._db.query(Source)
        if active_only:
            query = query.filter(Source.is_active == True)
        if search:
            escaped = search.replace("\\", "\\\\").replace("%", "\\%").replace("_", "\\_")
            query = query.filter(Source.name.ilike(f"%{escaped}%", escape="\\"))
        return self.get_all_paginated(query, Source.name, offset, limit)

    def get_by_name(self, name: str) -> Source | None:
        try:
            return self._db.query(Source).filter(Source.name == name).first()
        except SQLAlchemyError as e:
            raise DatabaseError(f"Failed to fetch source: {e}") from e
