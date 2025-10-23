from fastapi import APIRouter, Depends, HTTPException, status, Request
from fastapi.responses import RedirectResponse
from sqlalchemy.orm import Session

from ..config.database import get_db
from ..service.user_service import UserService
from ..schemas.schemas_user import UserBase

router = APIRouter(prefix="/api/users", tags=["users"])


@router.get("/login")
def login():
    """Generate Spotify login URL"""
    user_service = UserService()
    return user_service.get_auth_url()


@router.get("/callback")
def callback(code: str, request: Request, db: Session = Depends(get_db)):
    """Handle Spotify OAuth callback"""
    user_service = UserService(db)
    
    # Exchange authorization code for access token
    token_info = user_service.get_access_token(code)
    
    # Get user profile from Spotify
    user_profile = user_service.get_user_profile(token_info["access_token"])
    
    # Create or update user in database
    user = user_service.create_or_update_user(token_info, user_profile)
    
    # Return user data
    return UserBase.from_orm(user)


@router.get("/{user_id}")
def get_user(user_id: str, db: Session = Depends(get_db)):
    """Get user by ID"""
    user_service = UserService(db)
    user = user_service.get_user_by_id(user_id)
    return UserBase.from_orm(user)


@router.get("/spotify/{spotify_id}")
def get_user_by_spotify_id(spotify_id: str, db: Session = Depends(get_db)):
    """Get user by Spotify ID"""
    user_service = UserService(db)
    user = user_service.get_user_by_spotify_id(spotify_id)
    return UserBase.from_orm(user)


@router.post("/refresh-token/{user_id}")
def refresh_token(user_id: str, db: Session = Depends(get_db)):
    """Refresh access token for user"""
    user_service = UserService(db)
    user = user_service.get_user_by_id(user_id)
    
    # Refresh token
    token_info = user_service.refresh_access_token(user.refresh_token)
    
    # Update user with new tokens
    user.access_token = token_info.get("access_token")
    if token_info.get("refresh_token"):
        user.refresh_token = token_info.get("refresh_token")
    
    db.commit()
    db.refresh(user)
    
    return {"message": "Token refreshed successfully"}