from sqlalchemy import Boolean, Column, DateTime, Enum, ForeignKey, Integer, String, Text
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship

from ..config.database import Base


class UserModel(Base):
    __tablename__ = "user"

    spotify_id = Column(String(255), primary_key=True, unique=True)
    email = Column(String(255), nullable=False, unique=True)
    name = Column(String(255), nullable=False)
    access_token = Column(Text, nullable=True)
    refresh_token = Column(Text, nullable=True)
    created_at = Column(DateTime, nullable=False, default=func.now())
    updated_at = Column(DateTime, nullable=False, default=func.now(), onupdate=func.now())
    
    # Relationships
    playlists = relationship("PlaylistModel", back_populates="user", passive_deletes=True)