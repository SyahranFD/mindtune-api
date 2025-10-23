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
    Get current user from access token in Authorization header
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
    
    # Cari user berdasarkan access_token
    user = db.query(UserModel).filter(UserModel.access_token == access_token).first()
    
    if not user:
        # Debug: Cek apakah ada user dengan token yang mirip
        all_users = db.query(UserModel).all()
        print(f"Total users in DB: {len(all_users)}")
        for u in all_users:
            if u.access_token:
                print(f"User {u.id} token: {u.access_token[:10]}...")
        
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    print(f"Successfully authenticated user: {user.id}")
    return user