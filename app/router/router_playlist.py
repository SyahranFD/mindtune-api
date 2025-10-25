from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from app.config.database import get_db
from app.auth.auth import get_current_user
from app.model.user import UserModel
from app.schemas.schemas_playlist import PlaylistResponse, PlaylistUpdate
from app.service.service_playlist import create_playlist, get_all_playlists, get_playlist_by_id, update_playlist

router_playlist = APIRouter()


@router_playlist.post("/", response_model=PlaylistResponse, status_code=status.HTTP_201_CREATED)
async def create_playlist_endpoint(
    pre_mood: int,
    phq9: int,
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(get_current_user)
):
    """
    Create a new playlist based on user's mood and PHQ-9 score
    """
    playlist = create_playlist(db, current_user.spotify_id, pre_mood, phq9)
    return playlist


@router_playlist.put("/{playlist_id}", response_model=PlaylistResponse)
async def update_playlist_endpoint(
    playlist_id: str,
    playlist_data: PlaylistUpdate,
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(get_current_user)
):
    """
    Update a playlist with post_mood and/or feedback
    """
    # First check if the playlist exists and belongs to the current user
    playlist = get_playlist_by_id(db, playlist_id)
    
    if playlist.spotify_id != current_user.spotify_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to update this playlist"
        )
    
    # Update the playlist
    updated_playlist = update_playlist(
        db, 
        playlist_id, 
        post_mood=playlist_data.post_mood, 
        feedback=playlist_data.feedback
    )
    
    return updated_playlist


@router_playlist.get("/", response_model=List[PlaylistResponse])
async def get_all_playlists_endpoint(
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(get_current_user)
):
    """
    Get all playlists for the current user
    """
    playlists = get_all_playlists(db, current_user.spotify_id)
    return playlists


@router_playlist.get("/{playlist_id}", response_model=PlaylistResponse)
async def get_playlist_endpoint(
    playlist_id: str,
    db: Session = Depends(get_db),
    current_user: UserModel = Depends(get_current_user)
):
    """
    Get a specific playlist by ID
    """
    playlist = get_playlist_by_id(db, playlist_id)
    
    # Check if the playlist belongs to the current user
    if playlist.spotify_id != current_user.spotify_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to access this playlist"
        )
    
    return playlist