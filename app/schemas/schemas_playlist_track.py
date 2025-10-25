from datetime import datetime
from typing import Optional

from pydantic import BaseModel


class PlaylistTrackBase(BaseModel):
    id: str
    name: str
    artist: str
    duration: Optional[int] = None
    playlist_id: str
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class PlaylistTrackCreate(BaseModel):
    id: str
    name: str
    artist: str
    duration: Optional[int] = None
    playlist_id: str


class PlaylistTrackResponse(PlaylistTrackBase):
    @property
    def duration_minutes(self) -> Optional[float]:
        """Return the duration in minutes"""
        if self.duration is not None:
            return round(self.duration / 60000, 2)  # Convert ms to minutes and round to 2 decimal places
        return None