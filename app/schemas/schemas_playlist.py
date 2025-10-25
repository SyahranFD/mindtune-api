from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel

from .schemas_playlist_track import PlaylistTrackResponse
from .schemas_playlist_genre import PlaylistGenreResponse


class PlaylistBase(BaseModel):
    id: str
    spotify_id: str
    name: str
    phq9_score: Optional[int] = None
    depression_level: Optional[str] = None
    pre_mood: Optional[str] = None
    post_mood: Optional[str] = None
    duration: Optional[int] = None
    total_tracks: Optional[int] = None
    link_playlist: Optional[str] = None
    feedback: Optional[str] = None
    mode: Optional[str] = None

    class Config:
        from_attributes = True


class PlaylistCreate(BaseModel):
    id: str
    spotify_id: str
    name: str
    phq9_score: Optional[int] = None
    depression_level: Optional[str] = None
    pre_mood: Optional[str] = None
    post_mood: Optional[str] = None
    duration: Optional[int] = None
    total_tracks: Optional[int] = None
    link_playlist: Optional[str] = None
    feedback: Optional[str] = None
    mode: Optional[str] = None


class PlaylistUpdate(BaseModel):
    post_mood: Optional[str] = None
    feedback: Optional[str] = None


class PlaylistResponse(PlaylistBase):
    tracks: List[PlaylistTrackResponse] = []
    genres: List[PlaylistGenreResponse] = []