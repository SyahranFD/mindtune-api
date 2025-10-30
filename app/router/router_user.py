from fastapi import APIRouter, Depends
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
    refresh_token = token_info.get("refresh_token")

    user_profile = service_user.get_user_profile(access_token)

    # Create or update user in the database
    service_user.create_or_update_user(db, token_info, user_profile)

    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
    }

@router_user.get("/me")
def get_current_user_profile(
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    spotify_profile = service_user.get_user_profile(current_user.access_token)
    user = service_user.get_user_by_spotify_id(db, spotify_profile["id"])
    return UserBase.model_validate(user)

@router_user.get("/refresh-token")
def refresh_token(
    refresh_token: str,
    db: Session = Depends(get_db)
):
    # Get current user
    user = db.query(UserModel).filter(UserModel.refresh_token == refresh_token).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid refresh token",
        )

    # Refresh token
    token_info = service_user.refresh_access_token(refresh_token)

    # Update user with new tokens
    user.access_token = token_info.get("access_token")
    if token_info.get("refresh_token"):
        user.refresh_token = token_info.get("refresh_token")

    db.commit()
    db.refresh(user)

    return {
        "message": "Token refreshed successfully",
        "access_token": user.access_token,
        "refresh_token": user.refresh_token
    }
