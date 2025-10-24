"""create playlist genre table

Revision ID: 219eb77b8d08
Revises: 4d1732d1dc54
Create Date: 2025-10-24 17:09:05.420492

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '219eb77b8d08'
down_revision: Union[str, Sequence[str], None] = '4d1732d1dc54'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.create_table(
        "playlist_genre",
        sa.Column("id", sa.Integer, primary_key=True, autoincrement=True),
        sa.Column("playlist_id", sa.Integer, sa.ForeignKey("playlist.id"), nullable=False),
        sa.Column("name", sa.String(100), nullable=False),
        sa.Column("created_at", sa.DateTime, nullable=False, default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime, nullable=False, default=sa.func.now(), onupdate=sa.func.now()),
    )


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_table("playlist_genre")
