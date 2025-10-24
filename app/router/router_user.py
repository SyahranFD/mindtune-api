from fastapi import APIRouter, Depends, Security
from sqlalchemy.orm import Session

from ..config.database import get_db
from ..service import service_user
from ..schemas.schemas_user import UserBase
from ..auth.auth import get_current_user
from ..model.user import UserModel

router_user = APIRouter()


@router_user.get("/login")
def login():
    return service_user.get_auth_url()

@router_user.get("/access-token")
def get_access_token(
    code: str,
    db: Session = Depends(get_db)
):
    token_info = service_user.get_access_token(code)
    access_token = token_info["access_token"]
    user_profile = service_user.get_user_profile(access_token)

    # Create or update user in the database
    service_user.create_or_update_user(db, token_info, user_profile)
    
    return {
        "access_token": access_token,
        "token_type": "bearer"
    }

@router_user.get("/me")
def get_current_user_profile(
    db: Session = Depends(get_db),
    current_user=Security(get_current_user, scopes=["*"])
):
    spotify_profile = service_user.get_user_profile(current_user.access_token)
    user = service_user.get_user_by_spotify_id(db, spotify_profile["id"])
    return UserBase.model_validate(user)

@router_user.post("/refresh-token")
def refresh_token(current_user: UserModel = Depends(get_current_user), db: Session = Depends(get_db)):
    # Refresh token
    token_info = service_user.refresh_access_token(current_user.refresh_token)

    # Update user with new tokens
    current_user.access_token = token_info.get("access_token")
    if token_info.get("refresh_token"):
        current_user.refresh_token = token_info.get("refresh_token")

    db.commit()
    db.refresh(current_user)

    return {
        "message": "Token refreshed successfully",
        "access_token": current_user.access_token,
    }