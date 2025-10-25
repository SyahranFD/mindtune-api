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
    pass