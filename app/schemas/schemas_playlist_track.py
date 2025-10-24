from datetime import datetime
from typing import Optional

from pydantic import BaseModel


class PlaylistTrackBase(BaseModel):
    id: int
    name: str
    artist: str
    duration: Optional[int] = None
    playlist_id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class PlaylistTrackCreate(BaseModel):
    id: int
    name: str
    artist: str
    duration: Optional[int] = None
    playlist_id: int