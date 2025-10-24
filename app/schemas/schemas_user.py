from datetime import datetime
from typing import Optional

from pydantic import BaseModel, EmailStr


class UserBase(BaseModel):
    spotify_id: str
    email: Optional[EmailStr] = None
    name: Optional[str] = None
    access_token: Optional[str] = None
    refresh_token: Optional[str] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        orm_mode = True
        from_attributes = True


class UserCreate(BaseModel):
    spotify_id: str
    email: Optional[EmailStr] = None
    name: Optional[str] = None
    access_token: Optional[str] = None
    refresh_token: Optional[str] = None