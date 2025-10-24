"""create playlist track table

Revision ID: 3d551fa4491a
Revises: 219eb77b8d08
Create Date: 2025-10-24 17:09:15.683555

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '3d551fa4491a'
down_revision: Union[str, Sequence[str], None] = '219eb77b8d08'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.create_table(
        "playlist_track",
        sa.Column("id", sa.Integer, primary_key=True, autoincrement=True),
        sa.Column("name", sa.String(255), nullable=False),
        sa.Column("artist", sa.String(255), nullable=False),
        sa.Column("duration", sa.Integer, nullable=True),  # Duration in milliseconds
        sa.Column("playlist_id", sa.Integer, sa.ForeignKey("playlist.id"), nullable=False),
        sa.Column("created_at", sa.DateTime, nullable=False, default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime, nullable=False, default=sa.func.now(), onupdate=sa.func.now()),
    )


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_table("playlist_track")
