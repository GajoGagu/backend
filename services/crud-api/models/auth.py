from pydantic import BaseModel, Field
from typing import Optional
from .base import Address


class SignupRequest(BaseModel):
    email: str
    password: str = Field(..., min_length=8)
    name: str
    phone: str
    kakao_open_profile: str  # 카카오톡 오픈프로필 링크
    address: Address
    role: Optional[str] = "user"  # unified: user role, default to user


class LoginRequest(BaseModel):
    email: str
    password: str


class Tokens(BaseModel):
    token_type: str = "Bearer"
    access_token: str
    refresh_token: str
    expires_in: int = 3600


class User(BaseModel):
    id: str
    role: str = "user"
    email: str
    name: str
    phone: str
    address: Address
    kakao_open_profile: str
    created_at: str


class AuthResponse(BaseModel):
    user: User
    tokens: Tokens


class RefreshTokenRequest(BaseModel):
    refresh_token: str


class LogoutRequest(BaseModel):
    access_token: str


class UpdateUserRequest(BaseModel):
    name: Optional[str] = None
    phone: Optional[str] = None
    kakao_open_profile: Optional[str] = None
    address: Optional[Address] = None


class DeleteUserRequest(BaseModel):
    password: str  # 탈퇴 확인을 위한 비밀번호