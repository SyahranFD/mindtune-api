from sqlalchemy import Boolean, Column, DateTime, Enum, ForeignKey, Integer, String, Text
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship

from ..config.database import Base


class PlaylistTrackModel(Base):
    __tablename__ = "playlist_track"

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(255), nullable=False)
    artist = Column(String(255), nullable=False)
    duration = Column(Integer, nullable=True)  # Duration in milliseconds
    playlist_id = Column(Integer, ForeignKey("playlist.id", ondelete="CASCADE"), nullable=False)
    created_at = Column(DateTime, nullable=False, default=func.now())
    updated_at = Column(DateTime, nullable=False, default=func.now(), onupdate=func.now())

    # Relationships
    playlist = relationship("PlaylistModel", back_populates="tracks")