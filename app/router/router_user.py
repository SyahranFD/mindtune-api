from fastapi import APIRouter, Depends, HTTPException, status, Request
from fastapi.responses import RedirectResponse
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session

from ..config.database import get_db
from ..service.user_service import UserService
from ..schemas.schemas_user import UserBase
from ..auth.auth import get_current_user
from ..model.user import UserModel

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
    
    # Print token untuk debugging
    access_token = token_info["access_token"]
    print(f"Callback received token: {access_token[:10]}...")
    
    # Get user profile from Spotify
    user_profile = user_service.get_user_profile(access_token)
    
    # Create or update user in database
    user = user_service.create_or_update_user(token_info, user_profile)
    
    # Verifikasi token yang disimpan
    print(f"Stored token for user {user.id}: {user.access_token[:10]}...")
    
    # Return user data with access token for authentication
    user_data = UserBase.from_orm(user).dict()
    return {
        "user": user_data,
        "access_token": access_token,
        "token_type": "bearer"
    }


@router.get("/me", summary="Get Current User Profile", description="Get profile of the currently authenticated user. Example curl: `curl -X 'GET' 'http://127.0.0.1:8000/api/users/me' -H 'accept: application/json' -H 'Authorization: Bearer YOUR_ACCESS_TOKEN'`", responses={
    401: {"description": "Not authenticated"},
    200: {"description": "User profile"}
})
def get_current_user_profile(current_user: UserModel = Depends(get_current_user)):
    """Get current user profile"""
    # Debug: Print user info
    print(f"Returning profile for user: {current_user.id}")
    return UserBase.from_orm(current_user)


@router.get("/spotify/{spotify_id}")
def get_user_by_spotify_id(spotify_id: str, db: Session = Depends(get_db)):
    """Get user by Spotify ID"""
    user_service = UserService(db)
    user = user_service.get_user_by_spotify_id(spotify_id)
    return UserBase.from_orm(user)


@router.post("/refresh-token", summary="Refresh Access Token", description="Refresh the access token for the currently authenticated user. Example curl: `curl -X 'POST' 'http://127.0.0.1:8000/api/users/refresh-token' -H 'accept: application/json' -H 'Authorization: Bearer YOUR_ACCESS_TOKEN'`", responses={
    401: {"description": "Not authenticated"},
    200: {"description": "Token refreshed successfully"}
})
def refresh_token(current_user: UserModel = Depends(get_current_user), db: Session = Depends(get_db)):
    """Refresh access token for current user"""
    user_service = UserService(db)
    
    # Refresh token
    token_info = user_service.refresh_access_token(current_user.refresh_token)
    
    # Update user with new tokens
    current_user.access_token = token_info.get("access_token")
    if token_info.get("refresh_token"):
        current_user.refresh_token = token_info.get("refresh_token")
    
    db.commit()
    db.refresh(current_user)
    
    # Debug: Print token yang diperbarui
    print(f"Refreshed token for user {current_user.id}: {current_user.access_token[:10]}...")
    
    return {
        "message": "Token refreshed successfully", 
        "access_token": current_user.access_token,
        "token_type": "bearer"
    }