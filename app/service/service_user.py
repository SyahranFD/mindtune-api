import os
import uuid
from sqlalchemy.orm import Session
from fastapi import HTTPException
from spotipy import Spotify
from spotipy.oauth2 import SpotifyOAuth
from spotipy.cache_handler import CacheFileHandler
from dotenv import load_dotenv, find_dotenv

from app.model.user import UserModel
from app.schemas.schemas_user import UserCreate


load_dotenv(find_dotenv())
client_id = os.getenv("SP_CLIENT_ID")
client_secret = os.getenv("SP_CLIENT_SECRET")
redirect_uri = os.getenv("SP_REDIRECT_URI")
scope = os.getenv("SP_SCOPE")
sp_oauth = SpotifyOAuth(
    client_id=client_id,
    client_secret=client_secret,
    redirect_uri=redirect_uri,
    scope=scope,
    cache_handler=CacheFileHandler(cache_path=".spotify_cache"),
    show_dialog=True,
)


def get_auth_url():
    auth_url = sp_oauth.get_authorize_url()
    return {"auth_url": auth_url}

def get_access_token(code: str):
    token_info = sp_oauth.get_access_token(code)
    return token_info

def get_user_profile(access_token: str):
    sp = Spotify(auth=access_token)
    return sp.current_user()

def create_or_update_user(db: Session, token_info: dict, user_profile: dict):
    # Check if user exists by Spotify ID
    user = db.query(UserModel).filter(UserModel.spotify_id == user_profile["id"]).first()

    access_token = token_info.get("access_token")
    refresh_token = token_info.get("refresh_token")

    if not user:
        # Create new user
        user_data = UserCreate(
            spotify_id=user_profile.get("id"),
            email=user_profile.get("email"),
            name=user_profile.get("display_name"),
            access_token=access_token,
            refresh_token=refresh_token
        )
        user = UserModel(
            spotify_id=user_data.spotify_id,
            email=user_data.email or "",
            name=user_data.name or "",
            access_token=user_data.access_token,
            refresh_token=user_data.refresh_token
        )
        db.add(user)
        db.commit()
        db.refresh(user)
    else:
        # Update existing user
        user.name = user_profile.get("display_name", user.name)
        user.email = user_profile.get("email", user.email)
        user.access_token = access_token
        user.refresh_token = refresh_token if refresh_token else user.refresh_token

        db.commit()
        db.refresh(user)
    return user

def refresh_access_token(refresh_token: str):
    token_info = sp_oauth.refresh_access_token(refresh_token)
    return token_info

def get_user_by_spotify_id(db: Session, spotify_id: str):
    user = db.query(UserModel).filter(UserModel.spotify_id == spotify_id).first()
    if not user:
        raise HTTPException(status_code=404, detail=f"User with Spotify ID {spotify_id} not found")
    return user