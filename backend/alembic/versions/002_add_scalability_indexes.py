"""Add scalability indexes for alerts and events

Revision ID: 002
Revises: 001
Create Date: 2026-01-29

"""
from typing import Sequence, Union

from alembic import op


# revision identifiers, used by Alembic.
revision: str = '002'
down_revision: Union[str, None] = '001'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Composite indexes for alerts - common query patterns
    # These are low-cost since alerts are written infrequently (only on rule triggers)
    op.create_index(
        'ix_alerts_status_triggered_at',
        'alerts',
        ['status', 'triggered_at'],
        unique=False
    )
    op.create_index(
        'ix_alerts_rule_id_status',
        'alerts',
        ['rule_id', 'status'],
        unique=False
    )

def downgrade() -> None:
    op.drop_index('ix_alerts_rule_id_status', table_name='alerts')
    op.drop_index('ix_alerts_status_triggered_at', table_name='alerts')
