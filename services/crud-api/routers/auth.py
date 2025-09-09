import uuid
from datetime import datetime, timedelta
from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from models import SignupRequest, LoginRequest, AuthResponse, User, Rider, Tokens, RefreshTokenRequest, LogoutRequest, SocialLoginRequest
from database.config import get_db
from database.service import DatabaseService
from auth import hash_password, generate_token
from auth.social_auth import verify_social_token

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/users/signup", response_model=AuthResponse, status_code=201)
def signup_user(request: SignupRequest, db: Session = Depends(get_db)):
    service = DatabaseService(db)
    existing = service.get_user_by_email(request.email)
    if existing:
        raise HTTPException(status_code=400, detail="Email already exists")

    created = service.create_user(
        email=request.email,
        password=request.password,
        name=request.name,
        phone=request.phone,
    )

    access_token = generate_token()
    refresh_token = generate_token()
    service.add_active_token(user_id=created.id, token=access_token, expires_at=datetime.utcnow() + timedelta(hours=1))

    return AuthResponse(
        user=User(
            id=created.id,
            role=getattr(created, "role", "user"),
            email=created.email,
            name=created.name,
            phone=created.phone,
            address=created.address,
            created_at=created.created_at.isoformat() if created.created_at else datetime.utcnow().isoformat(),
        ),
        tokens=Tokens(
            access_token=access_token,
            refresh_token=refresh_token
        )
    )


@router.post("/users/login", response_model=AuthResponse)
def login_user(request: LoginRequest, db: Session = Depends(get_db)):
    service = DatabaseService(db)
    user = service.get_user_by_email(request.email)
    if not user or not service.verify_password(request.password, user.password_hash):
        raise HTTPException(status_code=401, detail="Invalid credentials")

    access_token = generate_token()
    refresh_token = generate_token()
    service.add_active_token(user_id=user.id, token=access_token, expires_at=datetime.utcnow() + timedelta(hours=1))

    return AuthResponse(
        user=User(
            id=user.id,
            role=getattr(user, "role", "user"),
            email=user.email,
            name=user.name,
            phone=user.phone,
            address=user.address,
            created_at=user.created_at.isoformat() if user.created_at else datetime.utcnow().isoformat(),
        ),
        tokens=Tokens(
            access_token=access_token,
            refresh_token=refresh_token
        )
    )


@router.post("/riders/signup", response_model=AuthResponse, status_code=201)
def signup_rider(request: SignupRequest):
    if request.email in riders_db:
        raise HTTPException(status_code=400, detail="Email already exists")
    
    rider_id = str(uuid.uuid4())
    rider = {
        "id": rider_id,
        "role": "rider",
        "email": request.email,
        "name": request.name,
        "phone": request.phone,
        "password_hash": hash_password(request.password),
        "vehicle_type": "car",
        "kakao_open_chat_url": "",
        "rating": 0.0,
        "created_at": datetime.now().isoformat()
    }
    riders_db[request.email] = rider
    
    access_token = generate_token()
    refresh_token = generate_token()
    
    active_tokens[access_token] = {
        "user": rider,
        "expires_at": datetime.now() + timedelta(hours=1)
    }
    
    return AuthResponse(
        user=Rider(**rider),
        tokens=Tokens(
            access_token=access_token,
            refresh_token=refresh_token
        )
    )


@router.post("/riders/login", response_model=AuthResponse)
def login_rider(request: LoginRequest):
    if request.email not in riders_db:
        raise HTTPException(status_code=401, detail="Invalid credentials")
    
    rider = riders_db[request.email]
    if rider["password_hash"] != hash_password(request.password):
        raise HTTPException(status_code=401, detail="Invalid credentials")
    
    access_token = generate_token()
    refresh_token = generate_token()
    
    active_tokens[access_token] = {
        "user": rider,
        "expires_at": datetime.now() + timedelta(hours=1)
    }
    
    return AuthResponse(
        user=Rider(**rider),
        tokens=Tokens(
            access_token=access_token,
            refresh_token=refresh_token
        )
    )


@router.post("/users/refresh", response_model=AuthResponse)
def refresh_user_token(request: RefreshTokenRequest, db: Session = Depends(get_db)):
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
        expires_at=datetime.utcnow() + timedelta(hours=1)
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
            created_at=user.created_at.isoformat() if user.created_at else datetime.utcnow().isoformat(),
        ),
        tokens=Tokens(
            access_token=new_access_token,
            refresh_token=new_refresh_token
        )
    )


@router.post("/users/logout")
def logout_user(request: LogoutRequest, db: Session = Depends(get_db)):
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


@router.post("/social/google", response_model=AuthResponse)
async def google_login(request: SocialLoginRequest, db: Session = Depends(get_db)):
    """Login with Google OAuth"""
    # Verify Google token
    social_user = await verify_social_token(request.access_token, "google")
    
    if not social_user:
        raise HTTPException(status_code=401, detail="Invalid Google token")
    
    service = DatabaseService(db)
    
    # Get or create user
    user = service.get_or_create_social_user(
        social_id=social_user.id,
        email=social_user.email,
        name=social_user.name,
        provider="google"
    )
    
    # Generate tokens
    access_token = generate_token()
    refresh_token = generate_token()
    service.add_active_token(
        user_id=user.id, 
        token=access_token, 
        expires_at=datetime.utcnow() + timedelta(hours=1)
    )
    
    return AuthResponse(
        user=User(
            id=user.id,
            role=getattr(user, "role", "user"),
            email=user.email,
            name=user.name,
            phone=user.phone,
            address=user.address,
            created_at=user.created_at.isoformat() if user.created_at else datetime.utcnow().isoformat(),
        ),
        tokens=Tokens(
            access_token=access_token,
            refresh_token=refresh_token
        )
    )


@router.post("/social/kakao", response_model=AuthResponse)
async def kakao_login(request: SocialLoginRequest, db: Session = Depends(get_db)):
    """Login with Kakao OAuth"""
    # Verify Kakao token
    social_user = await verify_social_token(request.access_token, "kakao")
    
    if not social_user:
        raise HTTPException(status_code=401, detail="Invalid Kakao token")
    
    service = DatabaseService(db)
    
    # Get or create user
    user = service.get_or_create_social_user(
        social_id=social_user.id,
        email=social_user.email,
        name=social_user.name,
        provider="kakao"
    )
    
    # Generate tokens
    access_token = generate_token()
    refresh_token = generate_token()
    service.add_active_token(
        user_id=user.id, 
        token=access_token, 
        expires_at=datetime.utcnow() + timedelta(hours=1)
    )
    
    return AuthResponse(
        user=User(
            id=user.id,
            role=getattr(user, "role", "user"),
            email=user.email,
            name=user.name,
            phone=user.phone,
            address=user.address,
            created_at=user.created_at.isoformat() if user.created_at else datetime.utcnow().isoformat(),
        ),
        tokens=Tokens(
            access_token=access_token,
            refresh_token=refresh_token
        )
    )
