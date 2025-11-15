from sqlalchemy import Boolean, Column, DateTime, Enum, ForeignKey, Integer, String, Text, UniqueConstraint
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship

from ..config.database import Base


class PlaylistModel(Base):
    __tablename__ = "playlist"
    __table_args__ = (
        UniqueConstraint('spotify_id', 'sequence_number', name='uq_playlist_user_seq'),
    )

    id = Column(Integer, primary_key=True, autoincrement=True)
    spotify_id = Column(String(255), ForeignKey("user.spotify_id"), nullable=False)
    name = Column(String(255), nullable=False)
    phq9_score = Column(Integer, nullable=True)
    depression_level = Column(String(50), nullable=True)
    pre_mood = Column(String(50), nullable=True)
    post_mood = Column(String(50), nullable=True)
    duration = Column(Integer, nullable=True)  # Duration in milliseconds
    total_tracks = Column(Integer, nullable=True)
    link_playlist = Column(String(255), nullable=True)
    feedback = Column(Text, nullable=True)
    mode = Column(String(50), nullable=True)
    sequence_number = Column(Integer, nullable=False)
    created_at = Column(DateTime, nullable=False, default=func.now())
    updated_at = Column(DateTime, nullable=False, default=func.now(), onupdate=func.now())

    # Relationships
    user = relationship("UserModel", back_populates="playlists")
    tracks = relationship("PlaylistTrackModel", back_populates="playlist")
    genres = relationship("PlaylistGenreModel", back_populates="playlist")