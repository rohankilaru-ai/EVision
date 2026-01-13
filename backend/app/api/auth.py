"""
Authentication API routes
"""
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session

from ..core.database import get_db
from ..services.auth import AuthService
from ..schemas.user import GoogleAuthRequest, TokenResponse, UserResponse
from ..models.user import User

router = APIRouter(prefix="/auth", tags=["Authentication"])
security = HTTPBearer()


@router.post("/google", response_model=TokenResponse)
async def google_auth(
    auth_request: GoogleAuthRequest,
    db: Session = Depends(get_db)
):
    """
    Authenticate user with Google OAuth

    Args:
        auth_request: Google auth code and redirect URI
    Returns:
        Access token, refresh token, and user data
    """
    # Verify Google token
    user_data = await AuthService.verify_google_token(auth_request.code)

    # Get or create user
    user = AuthService.get_or_create_user(db, user_data)

    # Create JWT tokens
    tokens = AuthService.create_tokens(user)

    return TokenResponse(
        access_token=tokens['access_token'],
        refresh_token=tokens['refresh_token'],
        token_type=tokens['token_type'],
        user=UserResponse.from_orm(user)
    )


@router.get("/me", response_model=UserResponse)
async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db)
):
    """
    Get current authenticated user

    Returns:
        Current user data
    """
    token = credentials.credentials
    user = AuthService.get_current_user(db, token)
    return UserResponse.from_orm(user)


@router.post("/refresh", response_model=TokenResponse)
async def refresh_token(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db)
):
    """
    Refresh access token using refresh token

    Returns:
        New access and refresh tokens
    """
    token = credentials.credentials
    user = AuthService.get_current_user(db, token)
    tokens = AuthService.create_tokens(user)

    return TokenResponse(
        access_token=tokens['access_token'],
        refresh_token=tokens['refresh_token'],
        token_type=tokens['token_type'],
        user=UserResponse.from_orm(user)
    )


def get_current_active_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db)
) -> User:
    """Dependency to get current active user"""
    token = credentials.credentials
    return AuthService.get_current_user(db, token)
