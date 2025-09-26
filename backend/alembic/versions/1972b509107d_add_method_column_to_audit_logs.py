"""Add method column to audit_logs

Revision ID: 1972b509107d
Revises: ac0a45778214
Create Date: 2025-09-26 17:34:08.182212
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = '1972b509107d'
down_revision: Union[str, Sequence[str], None] = 'ac0a45778214'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.add_column('audit_logs', sa.Column('method', sa.String(length=10), nullable=False, server_default='UNKNOWN'))
    op.add_column('audit_logs', sa.Column('path', sa.String(), nullable=False, server_default='/'))
    op.add_column('audit_logs', sa.Column('user_agent', sa.String(), nullable=True))

    op.drop_column('audit_logs', 'user_id')
    op.drop_column('audit_logs', 'details')
    op.drop_column('audit_logs', 'action')


def downgrade() -> None:
    """Downgrade schema."""
    # ✅ Add back with a default so old rows don’t break
    op.add_column(
        'audit_logs',
        sa.Column('action', sa.VARCHAR(), nullable=False, server_default='UNKNOWN')
    )
    op.add_column(
        'audit_logs',
        sa.Column('details', postgresql.JSON(astext_type=sa.Text()), nullable=True)
    )
    op.add_column('audit_logs', sa.Column('user_id', sa.UUID(), nullable=True))

    op.drop_column('audit_logs', 'user_agent')
    op.drop_column('audit_logs', 'path')
    op.drop_column('audit_logs', 'method')
