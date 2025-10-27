"""
Authentication routes
"""
from fastapi import APIRouter, status, Depends
from models.auth import RegisterRequest, LoginRequest, AuthResponse, TokenResponse
from services.auth_service import AuthService
from dependency.dependencies import get_auth_service
from middleware.auth import get_current_user


router = APIRouter(prefix="/api/auth", tags=["authentication"])


@router.post("/register", response_model=AuthResponse, status_code=status.HTTP_201_CREATED)
async def register(
    register_request: RegisterRequest,
    auth_service: AuthService = Depends(get_auth_service)
):
    """Register a new user"""
    return await auth_service.register(register_request)


@router.post("/login", response_model=AuthResponse)
async def login(
    login_request: LoginRequest,
    auth_service: AuthService = Depends(get_auth_service)
):
    """Login user"""
    return await auth_service.login(login_request)


@router.get("/verify", response_model=TokenResponse)
async def verify_token(
    current_user: str = Depends(get_current_user),
    auth_service: AuthService = Depends(get_auth_service)
):
    """Verify authentication token"""
    user = await auth_service.get_user(current_user)
    return TokenResponse(
        user_id=user['id'],
        email=user['email'],
        valid=True
    )


@router.get("/me")
async def get_current_user_info(
    current_user: str = Depends(get_current_user),
    auth_service: AuthService = Depends(get_auth_service)
):
    """Get current user information"""
    return await auth_service.get_user(current_user)
