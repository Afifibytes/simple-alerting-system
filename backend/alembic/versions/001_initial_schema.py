"""Initial schema

Revision ID: 001
Revises:
Create Date: 2024-01-01
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision: str = '001'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Create enum types
    condition_type = postgresql.ENUM('count', 'threshold', name='conditiontype', create_type=False)
    condition_type.create(op.get_bind(), checkfirst=True)

    severity_type = postgresql.ENUM('low', 'medium', 'high', name='severity', create_type=False)
    severity_type.create(op.get_bind(), checkfirst=True)

    alert_status = postgresql.ENUM('triggered', 'acknowledged', 'resolved', name='alertstatus', create_type=False)
    alert_status.create(op.get_bind(), checkfirst=True)

    channel_type = postgresql.ENUM('email', 'webhook', 'slack', name='channeltype', create_type=False)
    channel_type.create(op.get_bind(), checkfirst=True)

    # Sources table
    op.create_table(
        'sources',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('name', sa.String(255), nullable=False, unique=True),
        sa.Column('description', sa.String(1000), nullable=True),
        sa.Column('owner', sa.String(255), nullable=True),
        sa.Column('is_active', sa.Boolean(), nullable=False, default=True),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True),
    )
    op.create_index('ix_sources_name', 'sources', ['name'])
    op.create_index('ix_sources_is_active', 'sources', ['is_active'])

    # Events table
    op.create_table(
        'events',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('source_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('sources.id'), nullable=False),
        sa.Column('event_type', sa.String(255), nullable=False),
        sa.Column('data', postgresql.JSONB(), nullable=False),
        sa.Column('timestamp', sa.DateTime(timezone=True), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=True),
    )
    op.create_index('ix_events_source_id', 'events', ['source_id'])
    op.create_index('ix_events_timestamp', 'events', ['timestamp'])
    op.create_index('ix_events_source_timestamp', 'events', ['source_id', 'timestamp'])

    # Notification channels table
    op.create_table(
        'notification_channels',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('name', sa.String(255), nullable=False, unique=True),
        sa.Column('channel_type', postgresql.ENUM('email', 'webhook', 'slack', name='channeltype', create_type=False), nullable=False),
        sa.Column('config', postgresql.JSONB(), nullable=False),
        sa.Column('is_active', sa.Boolean(), nullable=False, default=True),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True),
    )
    op.create_index('ix_notification_channels_type', 'notification_channels', ['channel_type'])
    op.create_index('ix_notification_channels_is_active', 'notification_channels', ['is_active'])

    # Alert rules table
    op.create_table(
        'alert_rules',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('name', sa.String(255), nullable=False),
        sa.Column('source_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('sources.id'), nullable=False),
        sa.Column('condition_type', postgresql.ENUM('count', 'threshold', name='conditiontype', create_type=False), nullable=False),
        sa.Column('condition_field', sa.String(255), nullable=False),
        sa.Column('condition_operator', sa.String(10), nullable=False),
        sa.Column('condition_value', sa.String(255), nullable=False),
        sa.Column('condition_threshold', sa.Integer(), nullable=False),
        sa.Column('severity', postgresql.ENUM('low', 'medium', 'high', name='severity', create_type=False), nullable=False),
        sa.Column('time_window_seconds', sa.Integer(), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True),
    )
    op.create_index('ix_alert_rules_source_id', 'alert_rules', ['source_id'])
    op.create_index('ix_alert_rules_source_severity', 'alert_rules', ['source_id', 'severity'])

    # Alerts table
    op.create_table(
        'alerts',
        sa.Column('id', postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column('rule_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('alert_rules.id'), nullable=False),
        sa.Column('status', postgresql.ENUM('triggered', 'acknowledged', 'resolved', name='alertstatus', create_type=False), nullable=False),
        sa.Column('triggered_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('acknowledged_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('resolved_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('matches_count', sa.Integer(), nullable=False),
        sa.Column('severity', sa.String(20), nullable=False),
        sa.Column('message', sa.Text(), nullable=True),
    )
    op.create_index('ix_alerts_rule_id', 'alerts', ['rule_id'])
    op.create_index('ix_alerts_status', 'alerts', ['status'])
    op.create_index('ix_alerts_severity', 'alerts', ['severity'])
    op.create_index('ix_alerts_triggered_at', 'alerts', ['triggered_at'])

    # Junction table for rules <-> notification channels (many-to-many)
    op.create_table(
        'rule_notification_channels',
        sa.Column('rule_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('alert_rules.id'), primary_key=True),
        sa.Column('channel_id', postgresql.UUID(as_uuid=True), sa.ForeignKey('notification_channels.id'), primary_key=True),
    )


def downgrade() -> None:
    op.drop_table('rule_notification_channels')
    op.drop_table('alerts')
    op.drop_table('alert_rules')
    op.drop_table('notification_channels')
    op.drop_table('events')
    op.drop_table('sources')

    # Drop enum types
    op.execute('DROP TYPE IF EXISTS channeltype')
    op.execute('DROP TYPE IF EXISTS alertstatus')
    op.execute('DROP TYPE IF EXISTS severity')
    op.execute('DROP TYPE IF EXISTS conditiontype')
