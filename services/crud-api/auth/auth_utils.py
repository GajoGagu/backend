import hashlib
import secrets
from datetime import datetime, timedelta
from fastapi import Depends, HTTPException
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from database.config import get_db
from database.service import DatabaseService

security = HTTPBearer(auto_error=False)


def hash_password(password: str) -> str:
    """Hash password using SHA256 (use proper hashing in production)"""
    return hashlib.sha256(password.encode()).hexdigest()


def generate_token() -> str:
    """Generate a random token (use proper JWT in production)"""
    return secrets.token_urlsafe(32)


def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db)
) -> dict:
    """Get current authenticated user from token using DB-backed active tokens."""
    if credentials is None or not credentials.credentials:
        raise HTTPException(status_code=401, detail="Not authenticated")

    token = credentials.credentials
    service = DatabaseService(db)

    # Validate token
    if not service.is_token_active(token):
        raise HTTPException(status_code=401, detail="Invalid or expired token")

    user = service.get_user_from_token(token)
    if user is None:
        raise HTTPException(status_code=401, detail="Invalid or expired token")

    # Normalize to dict compatible with existing pydantic models
    role = getattr(user, "role", "user")
    data = {
        "id": user.id,
        "role": role,
        "email": user.email,
        "name": user.name,
        "phone": user.phone,
        "address": user.address,
        "created_at": user.created_at.isoformat() if user.created_at else None,
    }
    return data
