from datetime import datetime
from typing import Optional

from pydantic import BaseModel


class PlaylistGenreBase(BaseModel):
    id: int
    name: str
    playlist_id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class PlaylistGenreCreate(BaseModel):
    id: int
    name: str
    playlist_id: int