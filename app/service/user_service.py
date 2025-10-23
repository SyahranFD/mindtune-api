import os
import uuid
from datetime import datetime
from typing import Optional
from sqlalchemy.orm import Session
from fastapi import Depends, HTTPException, status
from spotipy import Spotify
from spotipy.oauth2 import SpotifyOAuth
from spotipy.cache_handler import CacheFileHandler

from ..config.database import get_db
from ..model.user import UserModel
from ..schemas.schemas_user import UserBase, UserCreate


class UserService:
    def __init__(self, db: Session = Depends(get_db)):
        self.db = db
        self.client_id = os.getenv("SP_CLIENT_ID")
        self.client_secret = os.getenv("SP_CLIENT_SECRET")
        self.redirect_uri = os.getenv("SP_REDIRECT_URI")
        self.scope = os.getenv("SP_SCOPE")
        self.auth_manager = SpotifyOAuth(
            client_id=self.client_id,
            client_secret=self.client_secret,
            redirect_uri=self.redirect_uri,
            scope=self.scope,
            cache_handler=CacheFileHandler(cache_path=".spotify_cache"),
            show_dialog=True,
        )

    def get_auth_url(self):
        """Generate Spotify authorization URL"""
        try:
            auth_url = self.auth_manager.get_authorize_url()
            return {"auth_url": auth_url}
        except Exception as e:
            # Membuat pesan error yang lebih sederhana dan mudah dibaca
            error_message = f"Gagal mendapatkan URL otorisasi: {str(e)}"
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=error_message
            )

    def get_access_token(self, code: str):
        """Exchange authorization code for access token"""
        try:
            token_info = self.auth_manager.get_access_token(code)
            return token_info
        except Exception as e:
            # Membuat pesan error yang lebih sederhana dan mudah dibaca
            error_message = f"Gagal mendapatkan token akses: {str(e).split('\n')[0]}"
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=error_message
            )

    def get_user_profile(self, access_token: str):
        """Get user profile from Spotify API"""
        try:
            sp = Spotify(auth=access_token)
            return sp.current_user()
        except Exception as e:
            # Membuat pesan error yang lebih sederhana dan mudah dibaca
            error_message = f"Gagal mendapatkan profil pengguna: {str(e).split('\n')[0]}"
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=error_message
            )

    def create_or_update_user(self, token_info: dict, user_profile: dict):
        """Create or update user in database"""
        # Check if user exists by Spotify ID
        user = self.db.query(UserModel).filter(UserModel.spotify_id == user_profile["id"]).first()
        
        if not user:
            # Create new user
            user_data = UserCreate(
                id=str(uuid.uuid4()),
                email=user_profile.get("email"),
                name=user_profile.get("display_name"),
                spotify_id=user_profile.get("id"),
                images_url=user_profile.get("images")[0].get("url") if user_profile.get("images") else None,
                access_token=token_info.get("access_token"),
                refresh_token=token_info.get("refresh_token")
            )
            
            user = UserModel(
                id=user_data.id,
                email=user_data.email,
                name=user_data.name,
                spotify_id=user_data.spotify_id,
                images_url=user_data.images_url,
                access_token=user_data.access_token,
                refresh_token=user_data.refresh_token
            )
            
            self.db.add(user)
            self.db.commit()
            self.db.refresh(user)
        else:
            # Update existing user
            user.name = user_profile.get("display_name", user.name)
            user.email = user_profile.get("email", user.email)
            user.images_url = user_profile.get("images")[0].get("url") if user_profile.get("images") else user.images_url
            user.access_token = token_info.get("access_token")
            user.refresh_token = token_info.get("refresh_token", user.refresh_token)
            
            self.db.commit()
            self.db.refresh(user)
        
        return user

    def refresh_access_token(self, refresh_token: str):
        """Refresh access token using refresh token"""
        try:
            token_info = self.auth_manager.refresh_access_token(refresh_token)
            return token_info
        except Exception as e:
            # Membuat pesan error yang lebih sederhana dan mudah dibaca
            error_message = f"Gagal menyegarkan token akses: {str(e).split('\n')[0]}"
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=error_message
            )

    def get_user_by_id(self, user_id: str):
        """Get user by ID"""
        user = self.db.query(UserModel).filter(UserModel.id == user_id).first()
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"User with ID {user_id} not found"
            )
        return user

    def get_user_by_spotify_id(self, spotify_id: str):
        """Get user by Spotify ID"""
        user = self.db.query(UserModel).filter(UserModel.spotify_id == spotify_id).first()
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"User with Spotify ID {spotify_id} not found"
            )
        return user