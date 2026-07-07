from fastapi import Request, HTTPException, status, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from jose import JWTError
from ..core.security import verify_token
from ..core.database import get_db
from ..models.user import User

security = HTTPBearer()

async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db)
) -> User:
    """Get current authenticated user from JWT token"""
    token = credentials.credentials
    
    # Verify token
    payload = verify_token(token)
    if payload is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication token",
            headers={"WWW-Authenticate": "Bearer"}
        )
    
    # Get user ID from token
    user_id = payload.get("sub")
    if user_id is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token payload",
            headers={"WWW-Authenticate": "Bearer"}
        )
    
    # Get user from database
    user = db.query(User).filter(User.id == user_id).first()
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found",
            headers={"WWW-Authenticate": "Bearer"}
        )
    
    # Check if user is active
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User account is deactivated"
        )
    
    return user

async def get_current_active_user(
    current_user: User = Depends(get_current_user)
) -> User:
    """Get current active user (additional check)"""
    if not current_user.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Inactive user"
        )
    return current_user

# Optional: Middleware to check authentication for all routes
class AuthMiddleware:
    def __init__(self, app, exclude_paths=None):
        self.app = app
        self.exclude_paths = exclude_paths or []
    
    async def __call__(self, scope, receive, send):
        if scope["type"] != "http":
            await self.app(scope, receive, send)
            return
        
        path = scope.get("path", "")
        
        # Skip auth for excluded paths
        if any(path.startswith(exclude) for exclude in self.exclude_paths):
            await self.app(scope, receive, send)
            return
        
        # Check for token in headers
        headers = dict(scope.get("headers", []))
        auth_header = headers.get(b"authorization")
        
        if auth_header:
            try:
                auth_str = auth_header.decode()
                if auth_str.startswith("Bearer "):
                    token = auth_str[7:]
                    payload = verify_token(token)
                    if payload:
                        # Add user info to scope
                        scope["user_id"] = payload.get("sub")
            except:
                pass
        
        await self.app(scope, receive, send)