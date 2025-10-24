"""create playlist table

Revision ID: 4d1732d1dc54
Revises: dfc80a96bef4
Create Date: 2025-10-24 17:08:36.802157

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '4d1732d1dc54'
down_revision: Union[str, Sequence[str], None] = 'dfc80a96bef4'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.create_table(
        "playlist",
        sa.Column("id", sa.String(255), primary_key=True),
        sa.Column("spotify_id", sa.String(255), sa.ForeignKey("user.spotify_id"), nullable=False),
        sa.Column("name", sa.String(255), nullable=False),
        sa.Column("phq9_score", sa.Integer, nullable=True),
        sa.Column("depression_level", sa.String(50), nullable=True),
        sa.Column("pre_mood", sa.String(50), nullable=True),
        sa.Column("post_mood", sa.String(50), nullable=True),
        sa.Column("duration", sa.Integer, nullable=True),
        sa.Column("total_tracks", sa.Integer, nullable=True),
        sa.Column("link_playlist", sa.String(255), nullable=True),
        sa.Column("feedback", sa.Text, nullable=True),
        sa.Column("mode", sa.String(50), nullable=True),
        sa.Column("created_at", sa.DateTime, nullable=False, default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime, nullable=False, default=sa.func.now(), onupdate=sa.func.now()),
    )


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_table("playlist")
