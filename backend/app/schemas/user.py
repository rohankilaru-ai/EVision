from pydantic import BaseModel, EmailStr
from typing import Optional
from datetime import datetime
from ..models.user import SubscriptionTier


class UserBase(BaseModel):
    email: EmailStr
    full_name: Optional[str] = None


class UserCreate(UserBase):
    google_id: str
    profile_picture: Optional[str] = None


class UserUpdate(BaseModel):
    full_name: Optional[str] = None
    profile_picture: Optional[str] = None


class UserInDB(UserBase):
    id: int
    google_id: Optional[str]
    profile_picture: Optional[str]
    subscription_tier: SubscriptionTier
    subscription_start_date: Optional[datetime]
    subscription_end_date: Optional[datetime]
    is_active: bool
    is_verified: bool
    created_at: datetime
    last_login: Optional[datetime]

    class Config:
        from_attributes = True


class UserResponse(UserInDB):
    """User response for API"""
    pass


class TokenResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    user: UserResponse


class GoogleAuthRequest(BaseModel):
    code: str
    redirect_uri: str
