import uuid
from datetime import datetime, timedelta
from fastapi import APIRouter, HTTPException, Depends
from models import SignupRequest, LoginRequest, AuthResponse, User, Rider, Tokens
from database import users_db, riders_db, active_tokens
from auth import hash_password, generate_token

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/users/signup", response_model=AuthResponse, status_code=201)
def signup_user(request: SignupRequest):
    if request.email in users_db:
        raise HTTPException(status_code=400, detail="Email already exists")
    
    user_id = str(uuid.uuid4())
    user = {
        "id": user_id,
        "role": "user",
        "email": request.email,
        "name": request.name,
        "phone": request.phone,
        "password_hash": hash_password(request.password),
        "created_at": datetime.now().isoformat()
    }
    users_db[request.email] = user
    
    access_token = generate_token()
    refresh_token = generate_token()
    
    active_tokens[access_token] = {
        "user": user,
        "expires_at": datetime.now() + timedelta(hours=1)
    }
    
    return AuthResponse(
        user=User(**user),
        tokens=Tokens(
            access_token=access_token,
            refresh_token=refresh_token
        )
    )


@router.post("/users/login", response_model=AuthResponse)
def login_user(request: LoginRequest):
    if request.email not in users_db:
        raise HTTPException(status_code=401, detail="Invalid credentials")
    
    user = users_db[request.email]
    if user["password_hash"] != hash_password(request.password):
        raise HTTPException(status_code=401, detail="Invalid credentials")
    
    access_token = generate_token()
    refresh_token = generate_token()
    
    active_tokens[access_token] = {
        "user": user,
        "expires_at": datetime.now() + timedelta(hours=1)
    }
    
    return AuthResponse(
        user=User(**user),
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
