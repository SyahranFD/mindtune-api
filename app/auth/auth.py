from fastapi import Depends, HTTPException, status, Header
from fastapi.security import OAuth2PasswordBearer, HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from typing import Optional

from ..config.database import get_db
from ..model.user import UserModel

# Untuk dokumentasi OpenAPI dan form login
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="api/users/login", auto_error=False)

# Untuk mengambil token dari header Authorization
security = HTTPBearer(auto_error=False)

# Untuk mengambil token langsung dari header Authorization tanpa prefix 'Bearer'
async def get_token_from_header(authorization: Optional[str] = Header(None)):
    if authorization:
        print(f"Raw Authorization header: {authorization}")
        if authorization.startswith("Bearer "):
            token = authorization.replace("Bearer ", "")
            print(f"Extracted token from header: {token[:10]}...")
            return token
    return None


async def get_current_user(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(security),
    token: Optional[str] = Depends(oauth2_scheme),
    header_token: Optional[str] = Depends(get_token_from_header),
    db: Session = Depends(get_db)
):
    """
    Get current user from access token in Authorization header and validate with Spotify API
    """
    # Coba dapatkan token dari berbagai sumber
    access_token = None
    
    # Prioritas: 1. Header langsung, 2. HTTPBearer, 3. OAuth2PasswordBearer
    if header_token:
        access_token = header_token
        print(f"Token from direct header: {access_token[:10] if access_token else None}")
    elif credentials:
        access_token = credentials.credentials
        print(f"Token from HTTPBearer: {access_token[:10] if access_token else None}")
    elif token:
        access_token = token
        print(f"Token from OAuth2: {access_token[:10] if access_token else None}")
    else:
        print("No token provided from any source")
    
    if not access_token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Debug: Print token untuk membantu troubleshooting
    print(f"Received token: {access_token[:10]}...")
    
    # Import di sini untuk menghindari circular import
    from ..service.user_service import UserService
    user_service = UserService(db)
    
    try:
        # Validasi token dengan Spotify API
        print(f"Validating token with Spotify API...")
        spotify_profile = user_service.get_user_profile(access_token)
        spotify_id = spotify_profile.get("id")
        
        if not spotify_id:
            print("Failed to get Spotify ID from profile")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid Spotify token",
                headers={"WWW-Authenticate": "Bearer"},
            )
            
        # Cari user berdasarkan spotify_id
        user = db.query(UserModel).filter(UserModel.spotify_id == spotify_id).first()
        
        if not user:
            print(f"User with Spotify ID {spotify_id} not found in database")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="User not found",
                headers={"WWW-Authenticate": "Bearer"},
            )
        
        # Update token di database jika berbeda
        if user.access_token != access_token:
            print(f"Updating access token for user {user.id}")
            user.access_token = access_token
            db.commit()
            db.refresh(user)
        
        print(f"Successfully authenticated user: {user.id} with Spotify ID: {spotify_id}")
        return user
        
    except Exception as e:
        print(f"Error validating token with Spotify API: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )