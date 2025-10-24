from sqlalchemy import Boolean, Column, DateTime, Enum, ForeignKey, Integer, String, Text
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship

from ..config.database import Base


class PlaylistGenreModel(Base):
    __tablename__ = "playlist_genre"

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(100), nullable=False)
    playlist_id = Column(Integer, ForeignKey("playlist.id"), nullable=False)
    spotify_id = Column(String(255), ForeignKey("user.spotify_id"), nullable=False)
    created_at = Column(DateTime, nullable=False, default=func.now())
    updated_at = Column(DateTime, nullable=False, default=func.now(), onupdate=func.now())

    # Relationships
    playlist = relationship("PlaylistModel", back_populates="genres")
    user = relationship("UserModel")