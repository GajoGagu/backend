import uuid
from datetime import datetime, timedelta, timezone
from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from models import SignupRequest, LoginRequest, AuthResponse, User, Tokens, RefreshTokenRequest, LogoutRequest
from database.config import get_db
from database.service import DatabaseService
from auth import hash_password, generate_token

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/signup", response_model=AuthResponse, status_code=201)
def signup(request: SignupRequest, db: Session = Depends(get_db)):
    service = DatabaseService(db)
    existing = service.get_user_by_email(request.email)
    if existing:
        raise HTTPException(status_code=400, detail="Email already exists")

    created = service.create_user(
        email=request.email,
        password=request.password,
        name=request.name,
        phone=request.phone,
        kakao_open_profile=request.kakao_open_profile,
        role=request.role or "user",
    )

    access_token = generate_token()
    refresh_token = generate_token()
    service.add_active_token(user_id=created.id, token=access_token, expires_at=datetime.now(timezone.utc) + timedelta(hours=1))
    service.add_active_token(user_id=created.id, token=refresh_token, expires_at=datetime.now(timezone.utc) + timedelta(days=7))

    return AuthResponse(
        user=User(
            id=created.id,
            role=getattr(created, "role", "user"),
            email=created.email,
            name=created.name,
            phone=created.phone,
            address=created.address,
            kakao_open_profile=created.kakao_open_profile,
            created_at=created.created_at.isoformat() if created.created_at else datetime.now(timezone.utc).isoformat(),
        ),
        tokens=Tokens(
            access_token=access_token,
            refresh_token=refresh_token
        )
    )


@router.post("/login", response_model=AuthResponse)
def login(request: LoginRequest, db: Session = Depends(get_db)):
    service = DatabaseService(db)
    user = service.get_user_by_email(request.email)
    if not user or not service.verify_password(request.password, user.password_hash):
        raise HTTPException(status_code=401, detail="Invalid credentials")

    access_token = generate_token()
    refresh_token = generate_token()
    service.add_active_token(user_id=user.id, token=access_token, expires_at=datetime.now(timezone.utc) + timedelta(hours=1))
    service.add_active_token(user_id=user.id, token=refresh_token, expires_at=datetime.now(timezone.utc) + timedelta(days=7))

    return AuthResponse(
        user=User(
            id=user.id,
            role=getattr(user, "role", "user"),
            email=user.email,
            name=user.name,
            phone=user.phone,
            address=user.address,
            kakao_open_profile=user.kakao_open_profile,
            created_at=user.created_at.isoformat() if user.created_at else datetime.now(timezone.utc).isoformat(),
        ),
        tokens=Tokens(
            access_token=access_token,
            refresh_token=refresh_token
        )
    )


## Legacy rider/user endpoints removed


## Legacy rider/user endpoints removed


@router.post("/refresh", response_model=AuthResponse)
def refresh_token(request: RefreshTokenRequest, db: Session = Depends(get_db)):
    """Refresh access token using refresh token"""
    service = DatabaseService(db)
    user = service.get_user_from_refresh_token(request.refresh_token)
    
    if not user:
        raise HTTPException(status_code=401, detail="Invalid refresh token")
    
    # Generate new tokens
    new_access_token = generate_token()
    new_refresh_token = generate_token()
    
    # Add new access token
    service.add_active_token(
        user_id=user.id, 
        token=new_access_token, 
        expires_at=datetime.now(timezone.utc) + timedelta(hours=1)
    )
    
    # Add new refresh token
    service.add_active_token(
        user_id=user.id, 
        token=new_refresh_token, 
        expires_at=datetime.now(timezone.utc) + timedelta(days=7)
    )
    
    # Remove old refresh token (simplified - in production, manage refresh tokens separately)
    service.remove_token(request.refresh_token)
    
    return AuthResponse(
        user=User(
            id=user.id,
            role=getattr(user, "role", "user"),
            email=user.email,
            name=user.name,
            phone=user.phone,
            address=user.address,
            kakao_open_profile=user.kakao_open_profile,
            created_at=user.created_at.isoformat() if user.created_at else datetime.now(timezone.utc).isoformat(),
        ),
        tokens=Tokens(
            access_token=new_access_token,
            refresh_token=new_refresh_token
        )
    )


@router.post("/logout")
def logout(request: LogoutRequest, db: Session = Depends(get_db)):
    """Logout user by revoking access token"""
    service = DatabaseService(db)
    
    # Verify token exists and get user
    user = service.get_user_from_token(request.access_token)
    if not user:
        raise HTTPException(status_code=401, detail="Invalid token")
    
    # Remove the specific token
    success = service.remove_token(request.access_token)
    
    if not success:
        raise HTTPException(status_code=400, detail="Token not found")
    
    return {"message": "Successfully logged out"}


