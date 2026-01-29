"""Repository for alert rule data access."""

from uuid import UUID

from sqlalchemy.orm import Session, joinedload
from sqlalchemy.exc import SQLAlchemyError

from app.exceptions import DatabaseError
from app.models.rule import AlertRule
from app.models.notification import NotificationChannel
from app.schemas.rule import AlertRuleCreate, AlertRuleUpdate


class RuleRepository:
    """Handles database operations for AlertRule with relationship management."""

    def __init__(self, db: Session):
        self._db = db

    def _base_query(self):
        """Query with eager loading for relationships."""
        return self._db.query(AlertRule).options(
            joinedload(AlertRule.source_rel),
            joinedload(AlertRule.notification_channels),
        )

    def create(self, rule: AlertRuleCreate, channels: list[NotificationChannel] | None = None) -> AlertRule:
        try:
            db_rule = AlertRule(**rule.model_dump(exclude={"notification_channel_ids"}))
            if channels:
                db_rule.notification_channels = channels
            self._db.add(db_rule)
            self._db.commit()
            self._db.refresh(db_rule)
            return db_rule
        except SQLAlchemyError as e:
            self._db.rollback()
            raise DatabaseError(f"Failed to create rule: {e}") from e

    def get_all(
        self,
        source_id: UUID | None = None,
        severity: str | None = None,
        offset: int = 0,
        limit: int = 50,
    ) -> tuple[list[AlertRule], int]:
        """Get paginated rules with optional filters. Uses single optimized query."""
        try:
            # Build base query with eager loading
            query = self._base_query()

            # Apply filters
            if source_id:
                query = query.filter(AlertRule.source_id == source_id)
            if severity:
                query = query.filter(AlertRule.severity == severity)

            # Count total (separate query but on filtered set, not fetching data)
            count_query = self._db.query(AlertRule.id)
            if source_id:
                count_query = count_query.filter(AlertRule.source_id == source_id)
            if severity:
                count_query = count_query.filter(AlertRule.severity == severity)
            total = count_query.count()

            # Fetch paginated results with eager loading
            items = (
                query
                .order_by(AlertRule.created_at.desc())
                .offset(offset)
                .limit(limit)
                .all()
            )
            return items, total
        except SQLAlchemyError as e:
            raise DatabaseError(f"Failed to fetch rules: {e}") from e

    def get_by_id(self, rule_id: UUID) -> AlertRule | None:
        try:
            return self._base_query().filter(AlertRule.id == rule_id).first()
        except SQLAlchemyError as e:
            raise DatabaseError(f"Failed to fetch rule: {e}") from e

    def get_by_source_id(self, source_id: UUID) -> list[AlertRule]:
        try:
            return self._base_query().filter(AlertRule.source_id == source_id).order_by(AlertRule.created_at.desc()).all()
        except SQLAlchemyError as e:
            raise DatabaseError(f"Failed to fetch rules: {e}") from e

    def update(self, rule_id: UUID, data: AlertRuleUpdate, channels: list[NotificationChannel] | None = None) -> AlertRule | None:
        try:
            rule = self.get_by_id(rule_id)
            if not rule:
                return None
            for field, value in data.model_dump(exclude={"notification_channel_ids"}, exclude_unset=True).items():
                setattr(rule, field, value)
            if channels is not None:
                rule.notification_channels = channels
            self._db.commit()
            self._db.refresh(rule)
            return rule
        except SQLAlchemyError as e:
            self._db.rollback()
            raise DatabaseError(f"Failed to update rule: {e}") from e

    def delete(self, rule_id: UUID) -> bool:
        try:
            rule = self.get_by_id(rule_id)
            if not rule:
                return False
            self._db.delete(rule)
            self._db.commit()
            return True
        except SQLAlchemyError as e:
            self._db.rollback()
            raise DatabaseError(f"Failed to delete rule: {e}") from e
