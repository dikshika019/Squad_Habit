from pydantic_settings import BaseSettings
from typing import Optional

class Settings(BaseSettings):
    DATABASE_URL: str = "sqlite:///./squad_habits.db"
    SECRET_KEY: str = "your-super-secret-key-change-this-in-production"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 10080
    GOOGLE_CLIENT_ID: str = "45030382566-nl1avotpm8jbfntbmel34eafc4e51l1d.apps.googleusercontent.com"
    GOOGLE_CLIENT_SECRET: str = "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"
    GOOGLE_REDIRECT_URI: str = "http://localhost:8000/api/auth/google/callback"
    FRONTEND_URL: str = "http://localhost:3000"
    PORT: int = 8000
    INVITE_EXPIRY_HOURS: int = 24
    
    class Config:
        env_file = ".env"
        case_sensitive = True

settings = Settings()