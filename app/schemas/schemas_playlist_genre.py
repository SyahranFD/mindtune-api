from datetime import datetime
from typing import Optional

from pydantic import BaseModel


class PlaylistGenreBase(BaseModel):
    name: str

    class Config:
        from_attributes = True


class PlaylistGenreCreate(BaseModel):
    id: str
    name: str
    playlist_id: str


class PlaylistGenreResponse(PlaylistGenreBase):
    pass