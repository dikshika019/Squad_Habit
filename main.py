from fastapi import FastAPI, Depends, HTTPException, status, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import RedirectResponse, JSONResponse
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel, EmailStr
from typing import Optional
from sqlalchemy import Uuid, create_engine, Column, String, DateTime, Boolean, func
from datetime import datetime, timedelta
import httpx
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
from jose import JWTError, jwt
from authlib.integrations.starlette_client import OAuth
from pydantic_settings import BaseSettings
import os
from uuid import uuid4

# ============ CONFIGURATION ============
class Settings(BaseSettings):
    DATABASE_URL: str = "sqlite:///./squad_habits.db"
    SECRET_KEY: str = "your-super-secret-key-change-this-in-production"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 10080
    GOOGLE_CLIENT_ID: str = ""
    GOOGLE_CLIENT_SECRET: str = ""
    GOOGLE_REDIRECT_URI: str = "http://localhost:8000/api/auth/google/callback"
    FRONTEND_URL: str = "http://localhost:3000"
    PORT: int = 8000
    
    class Config:
        env_file = ".env"
        case_sensitive = True

settings = Settings()

# ============ DATABASE ============
engine = create_engine(
    settings.DATABASE_URL,
    connect_args={"check_same_thread": False}
)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# ============ MODELS ============
class User(Base):
    __tablename__ = "users"
    
    id = Column(Uuid, primary_key=True, default=uuid4)
    google_id = Column(String, unique=True, nullable=True)
    email = Column(String, unique=True, index=True, nullable=False)
    name = Column(String, nullable=False)
    profile_picture = Column(String, nullable=True)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, onupdate=func.now())

# ============ SCHEMAS ============
class GoogleUserInfo(BaseModel):
    id: str
    email: EmailStr
    name: str
    picture: Optional[str] = None
    verified_email: Optional[bool] = False

class UserResponse(BaseModel):
    id: UUID
    email: EmailStr
    name: str
    profile_picture: Optional[str] = None
    is_active: bool
    created_at: datetime
    
    class Config:
        from_attributes = True

class LogoutResponse(BaseModel):
    message: str
    success: bool

# ============ SECURITY ============
def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
    return encoded_jwt

def verify_token(token: str) -> Optional[dict]:
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        return payload
    except JWTError:
        return None

# ============ MIDDLEWARE ============
security = HTTPBearer()

async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db)
) -> User:
    token = credentials.credentials
    payload = verify_token(token)
    
    if payload is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication token",
            headers={"WWW-Authenticate": "Bearer"}
        )
    
    user_id = payload.get("sub")
    if user_id is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token payload"
        )
    
    user = db.query(User).filter(User.id == user_id).first()
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found"
        )
    
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User account is deactivated"
        )
    
    return user

# ============ SERVICES ============
class AuthService:
    @staticmethod
    async def get_google_user_info(access_token: str) -> GoogleUserInfo:
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    "https://www.googleapis.com/oauth2/v2/userinfo",
                    headers={"Authorization": f"Bearer {access_token}"}
                )
                
                if response.status_code != 200:
                    raise HTTPException(
                        status_code=status.HTTP_400_BAD_REQUEST,
                        detail="Invalid Google token"
                    )
                
                data = response.json()
                return GoogleUserInfo(
                    id=data.get("id"),
                    email=data.get("email"),
                    name=data.get("name", "User"),
                    picture=data.get("picture"),
                    verified_email=data.get("verified_email", False)
                )
        except httpx.RequestError:
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="Failed to connect to Google API"
            )
    
    @staticmethod
    async def authenticate_or_create_user(google_user: GoogleUserInfo, db: Session) -> User:
        try:
            user = db.query(User).filter(User.google_id == google_user.id).first()
            
            if user:
                if user.name != google_user.name or user.profile_picture != google_user.picture:
                    user.name = google_user.name
                    user.profile_picture = google_user.picture
                    db.commit()
                    db.refresh(user)
                return user
            
            existing_user = db.query(User).filter(User.email == google_user.email).first()
            if existing_user:
                existing_user.google_id = google_user.id
                existing_user.name = google_user.name
                existing_user.profile_picture = google_user.picture
                db.commit()
                db.refresh(existing_user)
                return existing_user
            
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
            
        except Exception as e:
            db.rollback()
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"User creation failed: {str(e)}"
            )
    
    @staticmethod
    def create_user_token(user: User) -> dict:
        access_token = create_access_token(
            data={"sub": str(user.id), "email": user.email}
        )
        return {
            "access_token": access_token,
            "token_type": "bearer",
            "expires_in": settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
            "user_id": user.id
        }

# ============ ROUTES ============
oauth = OAuth()
oauth.register(
    name='google',
    client_id=settings.GOOGLE_CLIENT_ID,
    client_secret=settings.GOOGLE_CLIENT_SECRET,
    server_metadata_url='https://accounts.google.com/.well-known/openid-configuration',
    client_kwargs={
        'scope': 'openid email profile',
        'prompt': 'select_account'
    }
)

# Create FastAPI app
app = FastAPI(
    title="Squad Habits API",
    version="1.0.0",
    docs_url="/api/docs",
    redoc_url="/api/redoc"
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Create tables
Base.metadata.create_all(bind=engine)

# Routes
@app.get("/api/auth/google")
async def google_login(request: Request):
    redirect_uri = settings.GOOGLE_REDIRECT_URI
    return await oauth.google.authorize_redirect(request, redirect_uri)

@app.get("/api/auth/google/callback")
async def google_callback(request: Request, db: Session = Depends(get_db)):
    try:
        token = await oauth.google.authorize_access_token(request)
        if not token:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Failed to get access token from Google"
            )
        
        user_info = await AuthService.get_google_user_info(token["access_token"])
        user = await AuthService.authenticate_or_create_user(user_info, db)
        token_data = AuthService.create_user_token(user)
        
        redirect_url = f"{settings.FRONTEND_URL}/auth/callback?token={token_data['access_token']}"
        return RedirectResponse(url=redirect_url, status_code=status.HTTP_302_FOUND)
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"OAuth callback error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Authentication failed. Please try again."
        )

@app.get("/api/auth/me", response_model=UserResponse)
async def get_current_user_info(current_user: User = Depends(get_current_user)):
    return current_user

@app.post("/api/auth/logout", response_model=LogoutResponse)
async def logout(current_user: User = Depends(get_current_user)):
    return LogoutResponse(
        message="Logged out successfully",
        success=True
    )

@app.get("/api/auth/verify")
async def verify_token(current_user: User = Depends(get_current_user)):
    return {
        "valid": True,
        "user": {
            "id": str(current_user.id),
            "email": current_user.email,
            "name": current_user.name
        }
    }

@app.get("/api/auth/test")
async def test_auth(current_user: User = Depends(get_current_user)):
    return {
        "message": "Authentication successful!",
        "user": {
            "id": str(current_user.id),
            "email": current_user.email,
            "name": current_user.name,
            "profile_picture": current_user.profile_picture
        }
    }

@app.get("/api/health")
async def health_check():
    return JSONResponse(
        status_code=200,
        content={
            "status": "healthy",
            "message": "Squad Habits API is running",
            "version": "1.0.0"
        }
    )

@app.get("/")
async def root():
    return {
        "message": "Welcome to Squad Habits API",
        "docs": "/api/docs",
        "health": "/api/health"
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=settings.PORT,
        reload=True,
        log_level="info"
    )