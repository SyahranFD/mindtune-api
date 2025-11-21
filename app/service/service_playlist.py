import os
import json
import uuid
from datetime import datetime, timedelta
from typing import List, Optional, Dict
from sqlalchemy.orm import Session
from fastapi import HTTPException
import spotipy
from sqlalchemy import func
from collections import Counter

from app.model.playlist import PlaylistModel
from app.model.playlist_track import PlaylistTrackModel
from app.model.playlist_genre import PlaylistGenreModel
from app.model.user import UserModel
from app.schemas.schemas_playlist import PlaylistCreate, DashboardResponse, ChartMoodItem
from app.service.service_ai import build_prompt_playlist_healing, call_hf_api
from dotenv import load_dotenv, find_dotenv
from app.util.util_convert_time import calculate_time_ago


load_dotenv(find_dotenv())
def create_playlist(db: Session, spotify_id: str, pre_mood: int, phq9: int):
    user = db.query(UserModel).filter(UserModel.spotify_id == spotify_id).first()
    if not user:
        raise HTTPException(status_code=404, detail=f"User with Spotify ID {spotify_id} not found")
    
    sp = spotipy.Spotify(auth=user.access_token)
    
    # 1. Get user's top tracks
    try:
        top_tracks = sp.current_user_saved_tracks(limit=10, market="ID")
        top_ids = [item["track"]["uri"] for item in top_tracks["items"]]
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching top tracks: {str(e)}")
    
    # 2. Build prompt for AI
    prompt = build_prompt_playlist_healing(
        pre_mood=pre_mood,
        phq9=phq9,
        location="Indonesia",
        top_ids=top_ids
    )
    
    # 3. Call AI API
    try:
        ai_response = call_hf_api(prompt)
        ai_data = json.loads(ai_response)
    except Exception as e:
        raise HTTPException(
            status_code=500, 
            detail=f"Error calling AI API: {str(e)}" + f" HF_TOKEN: {os.getenv('HF_TOKEN')}"
        )
    
    # 4. Extract data from AI response
    title_ai = ai_data.get("playlist_title")
    description_ai = ai_data.get("description")
    playlist_ai = ai_data.get("playlist", [])
    genres_ai = ai_data.get("genres", [])
    
    print(ai_data)
    
    # 5. Create playlist in Spotify
    try:
        spotify_playlist = sp.user_playlist_create(
            user=user.spotify_id,
            name=title_ai,
            public=False,
            description=description_ai
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error creating Spotify playlist: {str(e)}")
    
    # 6. Search for tracks and add to playlist
    list_spotify_uri = []
    valid_tracks = []
    total_duration_ms = 0
    
    for track in playlist_ai:
        try:
            query = f"track:{track['title']} artist:{track['artist']}"
            search_result = sp.search(q=query, type="track", limit=1)
            
            if search_result["tracks"]["items"]:
                track_item = search_result["tracks"]["items"][0]
                track_uri = track_item["uri"]
                track_duration_ms = track_item["duration_ms"]
                total_duration_ms += track_duration_ms
                track["duration"] = track_duration_ms
                
                list_spotify_uri.append(track_uri)
                valid_tracks.append(track)
        except Exception as e:
            continue
    
    # 7. Add tracks to playlist
    if list_spotify_uri:
        try:
            sp.playlist_add_items(playlist_id=spotify_playlist["id"], items=list_spotify_uri)
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Error adding tracks to playlist: {str(e)}")
    
    # 8. Save to database
    playlist_id = str(uuid.uuid4())
    # Determine next sequence number per user
    last_seq = db.query(func.max(PlaylistModel.sequence_number)).filter(PlaylistModel.spotify_id == user.spotify_id).scalar()
    next_seq = (last_seq or 0) + 1
    
    # Determine depression level based on PHQ-9 score
    depression_level = ""
    if phq9 == 0:
        depression_level = "Tidak Ada Gejala"
    elif 1 <= phq9 <= 4:
        depression_level = "Minimal"
    elif 5 <= phq9 <= 9:
        depression_level = "Ringan"
    elif 10 <= phq9 <= 14:
        depression_level = "Sedang"
    elif 15 <= phq9 <= 19:
        depression_level = "Cukup Parah"
    elif phq9 >= 20:
        depression_level = "Parah"
    
    playlist_data = PlaylistCreate(
        id=playlist_id,
        spotify_id=user.spotify_id,
        name=title_ai,
        sequence_number=next_seq,
        phq9_score=phq9,
        depression_level=depression_level,
        pre_mood=str(pre_mood),
        total_tracks=len(valid_tracks),
        duration=total_duration_ms,
        link_playlist=spotify_playlist["external_urls"]["spotify"],
        mode="healing"
    )
    
    db_playlist = PlaylistModel(
        id=playlist_data.id,
        spotify_id=playlist_data.spotify_id,
        name=playlist_data.name,
        sequence_number=playlist_data.sequence_number,
        phq9_score=playlist_data.phq9_score,
        depression_level=playlist_data.depression_level,
        pre_mood=playlist_data.pre_mood,
        total_tracks=playlist_data.total_tracks,
        duration=playlist_data.duration,
        link_playlist=playlist_data.link_playlist,
        mode=playlist_data.mode
    )
    
    db.add(db_playlist)
    db.flush()
    
    # Add tracks
    for track in valid_tracks:
        track_id = str(uuid.uuid4())
        db_track = PlaylistTrackModel(
            id=track_id,
            name=track["title"],
            artist=track["artist"],
            duration=track.get("duration"),
            playlist_id=db_playlist.id
        )
        db.add(db_track)
    
    # Add genres
    for genre in genres_ai:
        genre_id = str(uuid.uuid4())
        db_genre = PlaylistGenreModel(
            id=genre_id,
            name=genre,
            playlist_id=db_playlist.id
        )
        db.add(db_genre)
    
    db.commit()
    db.refresh(db_playlist)
    
    db_playlist.time_ago = calculate_time_ago(db_playlist.created_at)
    
    return db_playlist


def get_all_playlists(db: Session, spotify_id: str):
    playlists = db.query(PlaylistModel).filter(PlaylistModel.spotify_id == spotify_id).order_by(PlaylistModel.sequence_number.desc()).all()
    
    for playlist in playlists:
        playlist.time_ago = calculate_time_ago(playlist.created_at)
    
    return playlists


def get_playlist_by_id(db: Session, playlist_id: str):
    playlist = db.query(PlaylistModel).filter(PlaylistModel.id == playlist_id).first()
    if not playlist:
        raise HTTPException(status_code=404, detail=f"Playlist with ID {playlist_id} not found")
    
    playlist.time_ago = calculate_time_ago(playlist.created_at)
    
    return playlist


def update_playlist(db: Session, playlist_id: str, post_mood: Optional[str] = None, feedback: Optional[str] = None):
    playlist = db.query(PlaylistModel).filter(PlaylistModel.id == playlist_id).first()
    if not playlist:
        raise HTTPException(status_code=404, detail=f"Playlist with ID {playlist_id} not found")
    
    if post_mood is not None:
        playlist.post_mood = post_mood
    
    if feedback is not None:
        playlist.feedback = feedback
    
    db.commit()
    db.refresh(playlist)
    
    return playlist

def delete_playlist(db: Session, playlist_id: str) -> None:
    playlist = db.query(PlaylistModel).filter(PlaylistModel.id == playlist_id).first()
    if not playlist:
        raise HTTPException(status_code=404, detail=f"Playlist with ID {playlist_id} not found")
    
    db.delete(playlist)
    db.commit()

def get_dashboard_data(db: Session, spotify_id: str) -> DashboardResponse:
    playlists = db.query(PlaylistModel).filter(PlaylistModel.spotify_id == spotify_id).all()
    
    total_sessions = len(playlists)
    
    if total_sessions == 0:
        return DashboardResponse(
            total_sessions=0,
            avg_mood_improvement=0.0,
            most_frequent_genre=None,
        )

    mood_improvements = []
    for playlist in playlists:
        if playlist.pre_mood is not None and playlist.post_mood is not None:
            try:
                pre_mood = int(playlist.pre_mood)
                post_mood = int(playlist.post_mood)
                mood_improvement = post_mood - pre_mood
                mood_improvements.append(mood_improvement)
            except (ValueError, TypeError):
                continue
    
    avg_mood_improvement = sum(mood_improvements) / len(mood_improvements) if mood_improvements else 0.0
    
    genres = db.query(PlaylistGenreModel).join(
        PlaylistModel, PlaylistGenreModel.playlist_id == PlaylistModel.id
    ).filter(
        PlaylistModel.spotify_id == spotify_id
    ).all()
    
    genre_counts = Counter([genre.name for genre in genres])
    
    most_frequent_genre = genre_counts.most_common(1)[0][0] if genre_counts else None
    
    return DashboardResponse(
        total_sessions=total_sessions,
        avg_mood_improvement=round(avg_mood_improvement, 2),
        most_frequent_genre=most_frequent_genre,
    )


def get_chart_mood(db: Session, spotify_id: str) -> List[ChartMoodItem]:
    playlists = (
        db.query(PlaylistModel)
        .filter(PlaylistModel.spotify_id == spotify_id)
        .order_by(PlaylistModel.sequence_number.asc())
        .all()
    )

    timeline: List[ChartMoodItem] = [
        ChartMoodItem(
            sequence_number=p.sequence_number,
            pre_mood=p.pre_mood,
            post_mood=p.post_mood,
        )
        for p in playlists
    ]

    return timeline