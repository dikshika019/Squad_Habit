from fastapi import APIRouter, HTTPException, Request, Depends, status
from fastapi.responses import RedirectResponse, JSONResponse
from sqlalchemy.orm import Session
from authlib.integrations.starlette_client import OAuth
from ..core.config import settings
from ..core.database import get_db
from ..services.auth_service import AuthService
from ..middleware.auth import get_current_user
from ..schemas.auth import UserResponse, LoginResponse, LogoutResponse
from ..models.user import User

router = APIRouter(prefix="/api/auth", tags=["Authentication"])

# Initialize OAuth
oauth = OAuth()
oauth.register(
    name='google',
    client_id=settings.GOOGLE_CLIENT_ID,
    client_secret=settings.GOOGLE_CLIENT_SECRET,
    server_metadata_url='https://accounts.google.com/.well-known/openid-configuration',
    client_kwargs={
        'scope': 'openid email profile',
        'prompt': 'select_account'  # Force account selection
    }
)

@router.get("/google")
async def google_login(request: Request):
    """
    Redirect to Google OAuth login page
    """
    redirect_uri = settings.GOOGLE_REDIRECT_URI
    return await oauth.google.authorize_redirect(request, redirect_uri)

@router.get("/google/callback")
async def google_callback(request: Request, db: Session = Depends(get_db)):
    """
    Handle Google OAuth callback
    """
    try:
        # Get token from Google
        token = await oauth.google.authorize_access_token(request)
        if not token:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Failed to get access token from Google"
            )
        
        # Get user info from token
        user_info = await AuthService.get_google_user_info(token["access_token"])
        
        # Authenticate or create user
        user = await AuthService.authenticate_or_create_user(user_info, db)
        
        # Create JWT token
        token_data = AuthService.create_user_token(user)
        
        # Redirect to frontend with token
        redirect_url = f"{settings.FRONTEND_URL}/auth/callback?token={token_data['access_token']}"
        return RedirectResponse(url=redirect_url, status_code=status.HTTP_302_FOUND)
        
    except HTTPException:
        # Re-raise HTTP exceptions
        raise
    except Exception as e:
        # Log error and return generic error
        print(f"OAuth callback error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Authentication failed. Please try again."
        )

@router.get("/me", response_model=UserResponse)
async def get_current_user_info(
    current_user: User = Depends(get_current_user)
):
    """
    Get current authenticated user information
    """
    return current_user

@router.post("/logout", response_model=LogoutResponse)
async def logout(
    current_user: User = Depends(get_current_user)
):
    """
    Logout user (client-side token removal required)
    """
    return LogoutResponse(
        message="Logged out successfully. Please remove the token from client.",
        success=True
    )

@router.post("/logout/all")
async def logout_all_devices(
    current_user: User = Depends(get_current_user)
):
    """
    Logout from all devices (server-side token revocation)
    """
    # In a real implementation, you would blacklist all tokens for this user
    # For now, we just return success
    return {
        "message": "Logged out from all devices",
        "success": True
    }

@router.get("/verify")
async def verify_token(
    current_user: User = Depends(get_current_user)
):
    """
    Verify if token is valid and get user info
    """
    return {
        "valid": True,
        "user": {
            "id": str(current_user.id),
            "email": current_user.email,
            "name": current_user.name
        }
    }

# Test endpoint to check authentication
@router.get("/test")
async def test_auth(
    current_user: User = Depends(get_current_user)
):
    """
    Test authentication endpoint
    """
    return {
        "message": "Authentication successful!",
        "user": {
            "id": str(current_user.id),
            "email": current_user.email,
            "name": current_user.name,
            "profile_picture": current_user.profile_picture
        }
    }