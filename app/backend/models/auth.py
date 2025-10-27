"""
Authentication models for user registration and login
"""
from pydantic import BaseModel, EmailStr, Field
from typing import Optional


class RegisterRequest(BaseModel):
    """Request model for user registration"""
    email: EmailStr
    password: str = Field(..., min_length=8, max_length=100)
    summoner_name: Optional[str] = Field(None, min_length=3, max_length=16)
    region: Optional[str] = Field(None, pattern="^(NA1|EUW1|EUN1|KR|BR1|JP1|LA1|LA2|OC1|TR1|RU)$")


class LoginRequest(BaseModel):
    """Request model for user login"""
    email: EmailStr
    password: str


class AuthResponse(BaseModel):
    """Response model for authentication"""
    user_id: str
    email: str
    token: str
    summoner_name: Optional[str] = None
    region: Optional[str] = None
    
    class Config:
        extra = "allow"


class TokenResponse(BaseModel):
    """Response model for token validation"""
    user_id: str
    email: str
    valid: bool
