from pydantic import BaseModel, Field
from typing import Optional
from .base import Address


class SignupRequest(BaseModel):
    email: str
    password: str = Field(..., min_length=8)
    name: Optional[str] = None
    phone: Optional[str] = None


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
    name: Optional[str] = None
    phone: Optional[str] = None
    address: Optional[Address] = None
    created_at: str


class AuthResponse(BaseModel):
    user: User
    tokens: Tokens
