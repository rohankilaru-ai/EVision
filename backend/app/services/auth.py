from google.oauth2 import id_token
from google.auth.transport import requests as google_requests
from sqlalchemy.orm import Session
from datetime import datetime
from typing import Optional, Dict, Any
from fastapi import HTTPException, status

from ..core.config import settings
from ..core.security import create_access_token, create_refresh_token, verify_token
from ..models.user import User, SubscriptionTier
from ..schemas.user import UserCreate


class AuthService:
    @staticmethod
    async def verify_google_token(token: str) -> Dict[str, Any]:
        """Verify Google OAuth token and extract user info"""
        try:
            idinfo = id_token.verify_oauth2_token(
                token,
                google_requests.Request(),
                settings.GOOGLE_CLIENT_ID
            )

            if idinfo['iss'] not in ['accounts.google.com', 'https://accounts.google.com']:
                raise ValueError('Wrong issuer.')

            return {
                'google_id': idinfo['sub'],
                'email': idinfo['email'],
                'full_name': idinfo.get('name'),
                'profile_picture': idinfo.get('picture'),
                'email_verified': idinfo.get('email_verified', False)
            }
        except ValueError as e:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail=f"Invalid Google token: {str(e)}"
            )

    @staticmethod
    def get_or_create_user(db: Session, user_data: Dict[str, Any]) -> User:
        """Get existing user or create new one from Google OAuth data"""
        user = db.query(User).filter(User.google_id == user_data['google_id']).first()

        if user:
            # Update last login
            user.last_login = datetime.utcnow()
            # Update profile info if changed
            if user_data.get('full_name'):
                user.full_name = user_data['full_name']
            if user_data.get('profile_picture'):
                user.profile_picture = user_data['profile_picture']
            db.commit()
            db.refresh(user)
        else:
            # Create new user
            user = User(
                email=user_data['email'],
                google_id=user_data['google_id'],
                full_name=user_data.get('full_name'),
                profile_picture=user_data.get('profile_picture'),
                subscription_tier=SubscriptionTier.FREE,
                is_verified=user_data.get('email_verified', False),
                last_login=datetime.utcnow()
            )
            db.add(user)
            db.commit()
            db.refresh(user)

        return user

    @staticmethod
    def create_tokens(user: User) -> Dict[str, str]:
        """Create access and refresh tokens for user"""
        token_data = {
            "sub": str(user.id),
            "email": user.email,
            "tier": user.subscription_tier.value
        }

        access_token = create_access_token(token_data)
        refresh_token = create_refresh_token(token_data)

        return {
            "access_token": access_token,
            "refresh_token": refresh_token,
            "token_type": "bearer"
        }

    @staticmethod
    def get_current_user(db: Session, token: str) -> User:
        """Get current user from JWT token"""
        payload = verify_token(token)
        user_id = payload.get("sub")

        if not user_id:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid authentication credentials"
            )

        user = db.query(User).filter(User.id == int(user_id)).first()
        if not user or not user.is_active:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="User not found or inactive"
            )

        return user

    @staticmethod
    def check_subscription_tier(user: User, required_tier: SubscriptionTier) -> bool:
        """Check if user has required subscription tier"""
        tier_hierarchy = {
            SubscriptionTier.FREE: 0,
            SubscriptionTier.PAID: 1
        }

        user_tier_level = tier_hierarchy.get(user.subscription_tier, 0)
        required_tier_level = tier_hierarchy.get(required_tier, 0)

        return user_tier_level >= required_tier_level
