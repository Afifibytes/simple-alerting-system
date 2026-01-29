"""Base repository with common CRUD operations."""

from typing import TypeVar, Generic, Type
from uuid import UUID

from pydantic import BaseModel
from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError

from app.exceptions import DatabaseError

T = TypeVar("T")  # SQLAlchemy model type


class BaseRepository(Generic[T]):
    """Base repository providing standard CRUD operations."""

    def __init__(self, db: Session, model: Type[T]):
        self._db = db
        self._model = model
        self._name = model.__name__

    def create(self, data: BaseModel, **extra) -> T:
        """Create a new entity."""
        try:
            obj = self._model(**data.model_dump(), **extra)
            self._db.add(obj)
            self._db.commit()
            self._db.refresh(obj)
            return obj
        except SQLAlchemyError as e:
            self._db.rollback()
            raise DatabaseError(f"Failed to create {self._name}: {e}") from e

    def get_by_id(self, id: UUID) -> T | None:
        """Get entity by ID."""
        try:
            return self._db.query(self._model).filter(self._model.id == id).first()
        except SQLAlchemyError as e:
            raise DatabaseError(f"Failed to fetch {self._name}: {e}") from e

    def update(self, id: UUID, data: BaseModel) -> T | None:
        """Update an entity. Returns None if not found."""
        try:
            obj = self.get_by_id(id)
            if not obj:
                return None
            for field, value in data.model_dump(exclude_unset=True).items():
                setattr(obj, field, value)
            self._db.commit()
            self._db.refresh(obj)
            return obj
        except SQLAlchemyError as e:
            self._db.rollback()
            raise DatabaseError(f"Failed to update {self._name}: {e}") from e

    def delete(self, id: UUID) -> bool:
        """Delete an entity. Returns True if deleted, False if not found."""
        try:
            obj = self.get_by_id(id)
            if not obj:
                return False
            self._db.delete(obj)
            self._db.commit()
            return True
        except SQLAlchemyError as e:
            self._db.rollback()
            raise DatabaseError(f"Failed to delete {self._name}: {e}") from e

    def get_all_paginated(self, query, order_by, offset: int = 0, limit: int = 50) -> tuple[list[T], int]:
        """Execute a query with pagination. Returns (items, total_count)."""
        try:
            total = query.count()
            items = query.order_by(order_by).offset(offset).limit(limit).all()
            return items, total
        except SQLAlchemyError as e:
            raise DatabaseError(f"Failed to fetch {self._name} list: {e}") from e
