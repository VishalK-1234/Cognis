"""create users table

Revision ID: 0a90b74632ea
Revises: 8d1a6b266101
Create Date: 2025-09-26 18:17:41.906359

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = '0a90b74632ea'
down_revision: Union[str, Sequence[str], None] = '8d1a6b266101'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

# ✅ define enum type
userrole = postgresql.ENUM('investigator', 'admin', name='userrole')


def upgrade() -> None:
    """Upgrade schema."""
    # explicitly create enum type
    userrole.create(op.get_bind(), checkfirst=True)

    # add column using the enum
    op.add_column(
        'users',
        sa.Column(
            'role',
            userrole,
            nullable=False,
            server_default='investigator'  # default role
        )
    )

    op.create_index(op.f('ix_users_id'), 'users', ['id'], unique=False)

    # drop old fields
    op.drop_column('users', 'is_active')
    op.drop_column('users', 'created_at')
    op.drop_column('users', 'is_superuser')


def downgrade() -> None:
    """Downgrade schema."""
    # restore old columns
    op.add_column('users', sa.Column('is_superuser', sa.BOOLEAN(), autoincrement=False, nullable=True))
    op.add_column('users', sa.Column('created_at', postgresql.TIMESTAMP(), autoincrement=False, nullable=True))
    op.add_column('users', sa.Column('is_active', sa.BOOLEAN(), autoincrement=False, nullable=True))

    op.drop_index(op.f('ix_users_id'), table_name='users')
    op.drop_column('users', 'role')

    # explicitly drop enum type
    userrole.drop(op.get_bind(), checkfirst=True)
