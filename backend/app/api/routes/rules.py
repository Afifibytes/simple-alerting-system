from uuid import UUID

from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session

from app.api.dependencies import get_db
from app.models.rule import Severity
from app.repositories.alert_repository import AlertRepository
from app.repositories.notification_repository import NotificationChannelRepository
from app.repositories.rule_repository import RuleRepository
from app.schemas.evaluation import EvaluationResponse
from app.schemas.pagination import PaginatedResponse
from app.schemas.rule import AlertRuleCreate, AlertRuleUpdate, AlertRuleResponse, AlertRuleDetailResponse
from app.services.rule_service import RuleService

router = APIRouter(prefix="/rules", tags=["Rules"])


def get_rule_service(db: Session = Depends(get_db)) -> RuleService:
    """Build rule service with its dependencies."""
    repository = RuleRepository(db)
    notification_repository = NotificationChannelRepository(db)
    alert_repository = AlertRepository(db)
    return RuleService(db, repository, notification_repository, alert_repository)


@router.post("", response_model=AlertRuleResponse, status_code=status.HTTP_201_CREATED)
async def create_rule(
    rule: AlertRuleCreate,
    service: RuleService = Depends(get_rule_service),
):
    """Create a new alert rule."""
    return service.create(rule)


def _rule_to_detail(rule) -> AlertRuleDetailResponse:
    """Convert AlertRule model to detailed response with source_name and channels."""
    from app.schemas.rule import NotificationChannelSummary
    return AlertRuleDetailResponse(
        id=rule.id,
        name=rule.name,
        source_id=rule.source_id,
        source_name=rule.source_rel.name if rule.source_rel else None,
        condition_type=rule.condition_type,
        condition_field=rule.condition_field,
        condition_operator=rule.condition_operator,
        condition_value=rule.condition_value,
        condition_threshold=rule.condition_threshold,
        severity=rule.severity,
        time_window_seconds=rule.time_window_seconds,
        created_at=rule.created_at,
        updated_at=rule.updated_at,
        notification_channels=[
            NotificationChannelSummary(id=ch.id, name=ch.name, channel_type=ch.channel_type)
            for ch in rule.notification_channels
        ],
    )


@router.get("", response_model=PaginatedResponse[AlertRuleDetailResponse])
async def list_rules(
    source_id: UUID | None = Query(None, description="Filter by source ID"),
    severity: Severity | None = Query(None, description="Filter by severity"),
    offset: int = Query(0, ge=0, description="Number of items to skip"),
    limit: int = Query(50, ge=1, le=1000, description="Maximum items to return"),
    service: RuleService = Depends(get_rule_service),
):
    """List alert rules with pagination and filtering."""
    items, total = service.get_all(
        source_id=source_id,
        severity=severity.value if severity else None,
        offset=offset,
        limit=limit,
    )
    return PaginatedResponse(
        items=[_rule_to_detail(rule) for rule in items],
        total=total,
        offset=offset,
        limit=limit,
        has_more=(offset + len(items)) < total,
    )


@router.get("/{rule_id}", response_model=AlertRuleDetailResponse)
async def get_rule(
    rule_id: UUID,
    service: RuleService = Depends(get_rule_service),
):
    """Get a specific alert rule by ID."""
    return _rule_to_detail(service.get_by_id(rule_id))


@router.patch("/{rule_id}", response_model=AlertRuleResponse)
async def update_rule(
    rule_id: UUID,
    rule_update: AlertRuleUpdate,
    service: RuleService = Depends(get_rule_service),
):
    """Update an alert rule."""
    return service.update(rule_id, rule_update)


@router.delete("/{rule_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_rule(
    rule_id: UUID,
    service: RuleService = Depends(get_rule_service),
):
    """Delete an alert rule."""
    service.delete(rule_id)


@router.post("/{rule_id}/evaluate", response_model=EvaluationResponse)
async def evaluate_rule(
    rule_id: UUID,
    create_alert: bool = Query(True, description="Create alert record if triggered"),
    service: RuleService = Depends(get_rule_service),
):
    """Evaluate a rule against current events."""
    return service.evaluate(rule_id, create_alert=create_alert)
