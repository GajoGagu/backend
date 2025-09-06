import hashlib
import secrets
from datetime import datetime
from fastapi import Depends, HTTPException
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from database import active_tokens

security = HTTPBearer()


def hash_password(password: str) -> str:
    """Hash password using SHA256 (use proper hashing in production)"""
    return hashlib.sha256(password.encode()).hexdigest()


def generate_token() -> str:
    """Generate a random token (use proper JWT in production)"""
    return secrets.token_urlsafe(32)


def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)) -> dict:
    """Get current authenticated user from token"""
    token = credentials.credentials
    if token not in active_tokens:
        raise HTTPException(status_code=401, detail="Invalid token")
    
    user_data = active_tokens[token]
    if user_data["expires_at"] < datetime.now():
        del active_tokens[token]
        raise HTTPException(status_code=401, detail="Token expired")
    
    return user_data["user"]
