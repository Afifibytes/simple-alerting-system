"""add avrage evaluation

Revision ID: 2b47094d3e69
Revises: 003
Create Date: 2026-02-05 13:10:15.225838
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '2b47094d3e69'
down_revision: Union[str, None] = '003'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.execute("ALTER TYPE conditiontype ADD VALUE 'average'")
    pass


def downgrade() -> None:
    op.execute("ALTER TYPE conditiontype DROP VALUE 'average'")
    pass
