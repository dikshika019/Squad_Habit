from pydantic import BaseModel, EmailStr
from typing import Optional
from uuid import UUID
from datetime import datetime

class GoogleUserInfo(BaseModel):
    """Google OAuth user info"""
    id: str
    email: EmailStr
    name: str
    picture: Optional[str] = None
    verified_email: Optional[bool] = False

class TokenResponse(BaseModel):
    """JWT token response"""
    access_token: str
    token_type: str = "bearer"
    expires_in: int
    user_id: UUID

class UserResponse(BaseModel):
    """User response schema"""
    id: UUID
    email: EmailStr
    name: str
    profile_picture: Optional[str] = None
    is_active: bool
    created_at: datetime
    
    class Config:
        from_attributes = True

class LoginResponse(BaseModel):
    """Full login response"""
    user: UserResponse
    token: TokenResponse

class LogoutResponse(BaseModel):
    """Logout response"""
    message: str
    success: bool