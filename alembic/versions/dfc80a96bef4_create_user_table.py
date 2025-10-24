"""create user table

Revision ID: dfc80a96bef4
Revises: 
Create Date: 2025-10-21 19:05:53.689216

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'dfc80a96bef4'
down_revision: Union[str, Sequence[str], None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.create_table(
        "user",
        sa.Column("spotify_id", sa.String(255), primary_key=True, unique=True),
        sa.Column("email", sa.String(255), nullable=False, unique=True),
        sa.Column("name", sa.String(255), nullable=False),
        sa.Column("access_token", sa.Text, nullable=True),
        sa.Column("refresh_token", sa.Text, nullable=True),
        sa.Column("created_at", sa.DateTime, nullable=False, default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime, nullable=False, default=sa.func.now(), onupdate=sa.func.now()),
    )


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_table("user")
