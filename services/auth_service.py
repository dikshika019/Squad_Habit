import httpx
from fastapi import HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from ..models.user import User
from ..schemas.auth import GoogleUserInfo
from ..core.security import create_access_token
from ..core.config import settings

class AuthService:
    @staticmethod
    async def get_google_user_info(access_token: str) -> GoogleUserInfo:
        """Fetch user info from Google using access token"""
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    "https://www.googleapis.com/oauth2/v2/userinfo",
                    headers={"Authorization": f"Bearer {access_token}"}
                )
                
                if response.status_code != 200:
                    raise HTTPException(
                        status_code=status.HTTP_400_BAD_REQUEST,
                        detail="Invalid Google token or unable to fetch user info"
                    )
                
                data = response.json()
                return GoogleUserInfo(
                    id=data.get("id"),
                    email=data.get("email"),
                    name=data.get("name", "User"),
                    picture=data.get("picture"),
                    verified_email=data.get("verified_email", False)
                )
        except httpx.RequestError as e:
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail=f"Failed to connect to Google API: {str(e)}"
            )
    
    @staticmethod
    async def authenticate_or_create_user(
        google_user: GoogleUserInfo,
        db: Session
    ) -> User:
        """Find existing user or create new one"""
        try:
            # Try to find user by google_id first
            user = db.query(User).filter(User.google_id == google_user.id).first()
            
            if user:
                # Update user info if needed
                if user.name != google_user.name or user.profile_picture != google_user.picture:
                    user.name = google_user.name
                    user.profile_picture = google_user.picture
                    db.commit()
                    db.refresh(user)
                return user
            
            # Check if user exists with same email (link accounts)
            existing_user = db.query(User).filter(User.email == google_user.email).first()
            if existing_user:
                # Link Google account to existing user
                existing_user.google_id = google_user.id
                existing_user.name = google_user.name
                existing_user.profile_picture = google_user.picture
                db.commit()
                db.refresh(existing_user)
                return existing_user
            
            # Create new user
            user = User(
                google_id=google_user.id,
                email=google_user.email,
                name=google_user.name,
                profile_picture=google_user.picture
            )
            db.add(user)
            db.commit()
            db.refresh(user)
            return user
            
        except IntegrityError:
            db.rollback()
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="User creation failed due to database integrity error"
            )
        except Exception as e:
            db.rollback()
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Authentication failed: {str(e)}"
            )
    
    @staticmethod
    def create_user_token(user: User) -> dict:
        """Create JWT token for user"""
        access_token = create_access_token(
            data={"sub": str(user.id), "email": user.email}
        )
        return {
            "access_token": access_token,
            "token_type": "bearer",
            "expires_in": settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
            "user_id": user.id
        }
    
    @staticmethod
    def get_user_by_id(user_id: str, db: Session) -> User:
        """Get user by ID"""
        user = db.query(User).filter(User.id == user_id).first()
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        return user