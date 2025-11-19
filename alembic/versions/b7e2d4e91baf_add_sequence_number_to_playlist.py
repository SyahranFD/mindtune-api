"""add sequence_number to playlist

Revision ID: b7e2d4e91baf
Revises: 4d1732d1dc54
Create Date: 2025-11-15 21:25:00

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'b7e2d4e91baf'
down_revision: Union[str, Sequence[str], None] = '3d551fa4491a'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema: add sequence_number column for playlist."""
    op.add_column(
        'playlist',
        sa.Column('sequence_number', sa.Integer(), nullable=False, server_default='1')
    )


def downgrade() -> None:
    """Downgrade schema: drop sequence_number column."""
    op.drop_column('playlist', 'sequence_number')