from datetime import datetime
from typing import List, Optional, Dict

from pydantic import BaseModel

from .schemas_playlist_track import PlaylistTrackResponse
from .schemas_playlist_genre import PlaylistGenreResponse


class PlaylistBase(BaseModel):
    id: str
    spotify_id: str
    name: str
    sequence_number: int
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
        json_encoders = {
            datetime: lambda dt: dt.strftime("%d/%m/%Y %H:%M")
        }


class PlaylistCreate(BaseModel):
    id: str
    spotify_id: str
    name: str
    sequence_number: int
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
    created_at: datetime
    time_ago: Optional[str] = None
    tracks: List[PlaylistTrackResponse] = []
    genres: List[PlaylistGenreResponse] = []


class DashboardResponse(BaseModel):
    total_sessions: int
    avg_mood_improvement: Optional[float] = None
    most_frequent_genre: Optional[str] = None

    class Config:
        from_attributes = True
        json_encoders = {
            datetime: lambda dt: dt.strftime("%d/%m/%Y %H:%M")
        }


class ChartMoodItem(BaseModel):
    sequence_number: int
    pre_mood: Optional[str] = None
    post_mood: Optional[str] = None

    class Config:
        from_attributes = True