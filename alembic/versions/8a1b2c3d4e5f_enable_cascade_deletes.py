"""enable cascade deletes on foreign keys

Revision ID: 8a1b2c3d4e5f
Revises: b7e2d4e91baf
Create Date: 2025-11-15 22:10:00

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "8a1b2c3d4e5f"
down_revision: Union[str, Sequence[str], None] = "b7e2d4e91baf"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema: set ON DELETE CASCADE on related foreign keys.

    Targets:
    - playlist.spotify_id -> user.spotify_id
    - playlist_track.playlist_id -> playlist.id
    - playlist_genre.playlist_id -> playlist.id
    """
    # playlist.spotify_id -> user.spotify_id
    op.drop_constraint("playlist_spotify_id_fkey", "playlist", type_="foreignkey")
    op.create_foreign_key(
        "playlist_spotify_id_fkey",
        source_table="playlist",
        referent_table="user",
        local_cols=["spotify_id"],
        remote_cols=["spotify_id"],
        ondelete="CASCADE",
    )

    # playlist_track.playlist_id -> playlist.id
    op.drop_constraint("playlist_track_playlist_id_fkey", "playlist_track", type_="foreignkey")
    op.create_foreign_key(
        "playlist_track_playlist_id_fkey",
        source_table="playlist_track",
        referent_table="playlist",
        local_cols=["playlist_id"],
        remote_cols=["id"],
        ondelete="CASCADE",
    )

    # playlist_genre.playlist_id -> playlist.id
    op.drop_constraint("playlist_genre_playlist_id_fkey", "playlist_genre", type_="foreignkey")
    op.create_foreign_key(
        "playlist_genre_playlist_id_fkey",
        source_table="playlist_genre",
        referent_table="playlist",
        local_cols=["playlist_id"],
        remote_cols=["id"],
        ondelete="CASCADE",
    )


def downgrade() -> None:
    """Downgrade schema: restore foreign keys without ON DELETE CASCADE."""
    # playlist.spotify_id -> user.spotify_id (remove cascade)
    op.drop_constraint("playlist_spotify_id_fkey", "playlist", type_="foreignkey")
    op.create_foreign_key(
        "playlist_spotify_id_fkey",
        source_table="playlist",
        referent_table="user",
        local_cols=["spotify_id"],
        remote_cols=["spotify_id"],
        ondelete=None,
    )

    # playlist_track.playlist_id -> playlist.id (remove cascade)
    op.drop_constraint("playlist_track_playlist_id_fkey", "playlist_track", type_="foreignkey")
    op.create_foreign_key(
        "playlist_track_playlist_id_fkey",
        source_table="playlist_track",
        referent_table="playlist",
        local_cols=["playlist_id"],
        remote_cols=["id"],
        ondelete=None,
    )

    # playlist_genre.playlist_id -> playlist.id (remove cascade)
    op.drop_constraint("playlist_genre_playlist_id_fkey", "playlist_genre", type_="foreignkey")
    op.create_foreign_key(
        "playlist_genre_playlist_id_fkey",
        source_table="playlist_genre",
        referent_table="playlist",
        local_cols=["playlist_id"],
        remote_cols=["id"],
        ondelete=None,
    )