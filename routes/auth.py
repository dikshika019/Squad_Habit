import uuid
import httpx

from urllib.parse import urlencode

from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
    status,
    Request
)

from fastapi.responses import RedirectResponse, JSONResponse

from sqlalchemy.orm import Session

from database import get_db
from models import User
from schemas import UserResponse
from auth import (
    create_access_token,
    get_current_user,
    get_google_user_info
)
from config import settings

router = APIRouter()


# -----------------------------
# Google Login
# -----------------------------
@router.get("/google")
async def google_login():

    state = str(uuid.uuid4())

    params = {
        "client_id": settings.GOOGLE_CLIENT_ID,
        "redirect_uri": settings.GOOGLE_REDIRECT_URI,
        "response_type": "code",
        "scope": "openid email profile",
        "access_type": "offline",
        "prompt": "select_account",
        "state": state
    }

    auth_url = (
        "https://accounts.google.com/o/oauth2/v2/auth?"
        + urlencode(params)
    )

    return RedirectResponse(auth_url)


# -----------------------------
# Google Callback
# -----------------------------
@router.get("/google/callback")
async def google_callback(
    request: Request,
    code: str = None,
    error: str = None,
    db: Session = Depends(get_db)
):

    if error:

        raise HTTPException(
            status_code=400,
            detail=error
        )

    if code is None:

        raise HTTPException(
            status_code=400,
            detail="Authorization code missing."
        )

    token_url = "https://oauth2.googleapis.com/token"

    token_data = {
        "client_id": settings.GOOGLE_CLIENT_ID,
        "client_secret": settings.GOOGLE_CLIENT_SECRET,
        "code": code,
        "grant_type": "authorization_code",
        "redirect_uri": settings.GOOGLE_REDIRECT_URI
    }

    async with httpx.AsyncClient() as client:

        token_response = await client.post(
            token_url,
            data=token_data
        )

    if token_response.status_code != 200:

        raise HTTPException(
            status_code=400,
            detail="Unable to fetch Google token."
        )

    token_json = token_response.json()

    google_access_token = token_json.get("access_token")

    if google_access_token is None:

        raise HTTPException(
            status_code=400,
            detail="Google access token missing."
        )

    google_user = await get_google_user_info(
        google_access_token
    )

    user = db.query(User).filter(
        User.email == google_user.email
    ).first()

    if user is None:

        user = User(
            google_id=google_user.id,
            name=google_user.name,
            email=google_user.email,
            profile_picture=google_user.picture
        )

        db.add(user)
        db.commit()
        db.refresh(user)

    else:

        user.google_id = google_user.id
        user.name = google_user.name
        user.profile_picture = google_user.picture

        db.commit()
        db.refresh(user)

    access_token = create_access_token(

        {
            "sub": str(user.id),
            "email": user.email
        }

    )

    response = RedirectResponse(
        url="/dashboard",
        status_code=status.HTTP_302_FOUND
    )

    response.set_cookie(
        key="access_token",
        value=access_token,
        httponly=True,
        samesite="lax",
        secure=False
    )

    return response


# -----------------------------
# Current User
# -----------------------------
# In routes/auth.py

# In routes/auth.py

@router.get("/me", response_model=UserResponse)
async def me(
    request: Request,
    db: Session = Depends(get_db)
):
    """
    Get current user information
    """
    try:
        # get_current_user will raise exception if not authenticated
        current_user = await get_current_user(request, db)
        
        # Return user data
        return UserResponse(
            id=current_user.id,
            name=current_user.name,
            email=current_user.email,
            profile_picture=current_user.profile_picture
        )
        
    except HTTPException:
        # Re-raise HTTP exceptions (401, 403, etc.)
        raise
    except Exception as e:
        print(f"[ERROR] Unexpected error in /me: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error fetching user: {str(e)}"
        )
# -----------------------------
# Verify Token
# -----------------------------
@router.get("/verify")
async def verify(

    current_user: User = Depends(
        get_current_user
    )

):

    return {
        "success": True,
        "user": {
            "id": current_user.id,
            "name": current_user.name,
            "email": current_user.email
        }
    }


# -----------------------------
# Logout
# -----------------------------
@router.post("/logout")
async def logout(

    current_user: User = Depends(
        get_current_user
    )

):

    response = JSONResponse(

        content={
            "success": True,
            "message": "Logged out successfully."
        }

    )

    response.delete_cookie("access_token")

    return response