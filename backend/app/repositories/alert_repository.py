"""Repository for alert data access."""

from datetime import datetime, timezone
from uuid import UUID

from sqlalchemy.orm import Session, joinedload
from sqlalchemy.exc import SQLAlchemyError

from app.exceptions import DatabaseError
from app.models.alert import Alert, AlertStatus
from app.models.rule import AlertRule


class AlertRepository:
    def __init__(self, db: Session):
        self._db = db

    def create(self, rule: AlertRule, matches_count: int, message: str | None = None) -> Alert:
        try:
            alert = Alert(rule_id=rule.id, matches_count=matches_count, severity=rule.severity.value, message=message)
            self._db.add(alert)
            self._db.commit()
            self._db.refresh(alert)
            return alert
        except SQLAlchemyError as e:
            self._db.rollback()
            raise DatabaseError(f"Failed to create alert: {e}") from e

    def get_all(
        self,
        rule_id: UUID | None = None,
        status: AlertStatus | None = None,
        severity: str | None = None,
        offset: int = 0,
        limit: int = 50,
    ) -> tuple[list[type[Alert]], int]:
        try:
            query = self._db.query(Alert).options(joinedload(Alert.rule))
            if rule_id:
                query = query.filter(Alert.rule_id == rule_id)
            if status:
                query = query.filter(Alert.status == status)
            if severity:
                query = query.filter(Alert.severity == severity)
            total = query.count()
            items = query.order_by(Alert.triggered_at.desc()).offset(offset).limit(limit).all()
            return items, total
        except SQLAlchemyError as e:
            raise DatabaseError(f"Failed to fetch alerts: {e}") from e

    def get_by_id(self, alert_id: UUID) -> Alert | None:
        try:
            return self._db.query(Alert).options(joinedload(Alert.rule)).filter(Alert.id == alert_id).first()
        except SQLAlchemyError as e:
            raise DatabaseError(f"Failed to fetch alert: {e}") from e

    def _update_status(self, alert_id: UUID, status: AlertStatus, timestamp_field: str) -> Alert | None:
        try:
            alert = self.get_by_id(alert_id)
            if not alert:
                return None
            alert.status = status
            setattr(alert, timestamp_field, datetime.now(timezone.utc))
            self._db.commit()
            self._db.refresh(alert)
            return alert
        except SQLAlchemyError as e:
            self._db.rollback()
            raise DatabaseError(f"Failed to update alert: {e}") from e

    def acknowledge(self, alert_id: UUID) -> Alert | None:
        return self._update_status(alert_id, AlertStatus.acknowledged, "acknowledged_at")

    def resolve(self, alert_id: UUID, message: str | None = None) -> Alert | None:
        alert = self._update_status(alert_id, AlertStatus.resolved, "resolved_at")
        if alert and message:
            alert.message = message
            self._db.commit()
            self._db.refresh(alert)
        return alert
