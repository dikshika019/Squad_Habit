# In auth.py

from datetime import datetime, timedelta
from typing import Optional
import httpx
from jose import jwt, JWTError
from fastapi import HTTPException, status, Depends, Request
from sqlalchemy.orm import Session
from database import get_db
from config import settings
from models import User
from schemas import GoogleUserInfo


def create_access_token(
    data: dict,
    expires_delta: Optional[timedelta] = None
):
    to_encode = data.copy()
    
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(
            minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES
        )
    
    to_encode.update({"exp": expire})
    
    return jwt.encode(
        to_encode,
        settings.SECRET_KEY,
        algorithm=settings.ALGORITHM
    )


def verify_token(token: str):
    try:
        payload = jwt.decode(
            token,
            settings.SECRET_KEY,
            algorithms=[settings.ALGORITHM]
        )
        return payload
    except JWTError:
        return None


async def get_current_user(
    request: Request,
    db: Session = Depends(get_db)
):
    """
    Get current user from JWT token in cookie.
    Returns User object or raises HTTPException.
    """
    # Debug prints
    print("[DEBUG] Cookies:", request.cookies)
    
    # Get token from cookie
    token = request.cookies.get("access_token")
    print("[DEBUG] Token:", token[:20] + "..." if token else "None")
    
    # Check if token exists
    if not token:
        print("[DEBUG] No token found")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated - no token"
        )
    
    # Verify token
    payload = verify_token(token)
    print("[DEBUG] Payload:", payload)
    
    # Check if token is valid
    if not payload:
        print("[DEBUG] Invalid token")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token"
        )
    
    # Get user ID from payload
    user_id = payload.get("sub")
    print("[DEBUG] User ID from token:", user_id)
    
    if not user_id:
        print("[DEBUG] No user_id in token")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token - no user ID"
        )
    
    # Get user from database
    try:
        user = db.query(User).filter(User.id == user_id).first()
        print("[DEBUG] User found:", user.email if user else "None")
    except Exception as e:
        print(f"[DEBUG] Database error: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Database error"
        )
    
    # Check if user exists
    if not user:
        print("[DEBUG] User not found in database")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found"
        )
    
    print("[DEBUG] Authentication successful!")
    return user


async def get_google_user_info(access_token: str):
    async with httpx.AsyncClient() as client:
        response = await client.get(
            "https://www.googleapis.com/oauth2/v2/userinfo",
            headers={
                "Authorization": f"Bearer {access_token}"
            }
        )
        
        if response.status_code != 200:
            raise HTTPException(
                status_code=400,
                detail="Invalid Google Token"
            )
        
        data = response.json()
        
        return GoogleUserInfo(
            id=data["id"],
            email=data["email"],
            name=data["name"],
            picture=data.get("picture"),
            verified_email=data.get("verified_email", False)
        )