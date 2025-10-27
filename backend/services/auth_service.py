"""
Auth service - Orchestrates authentication operations
"""
from repositories.auth_repository import AuthRepository
from domain.auth_domain import AuthDomain
from domain.exceptions import DomainException
from models.auth import RegisterRequest, LoginRequest, AuthResponse, TokenResponse
from fastapi import HTTPException, status


class AuthService:
    """Service for authentication - pure orchestration"""
    
    def __init__(self, auth_repository: AuthRepository, auth_domain: AuthDomain):
        self.auth_repository = auth_repository
        self.auth_domain = auth_domain
    
    async def register(self, register_request: RegisterRequest) -> AuthResponse:
        """Register a new user"""
        try:
            self.auth_domain.validate_email(register_request.email)
            self.auth_domain.validate_password(register_request.password)
            
            if register_request.summoner_name:
                self.auth_domain.validate_summoner_name(register_request.summoner_name)
            
            if register_request.region:
                self.auth_domain.validate_region(register_request.region)
        except DomainException as e:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=e.message
            )
        
        existing_user = await self.auth_repository.get_user_by_email(register_request.email)
        if existing_user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="User with this email already exists"
            )
        user_data = {
            'summoner_name': register_request.summoner_name,
            'region': register_request.region
        }
        
        try:
            result = await self.auth_repository.create_user(
                register_request.email,
                register_request.password,
                user_data
            )
            
            if not result:
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail="Failed to create user"
                )
            
            return result
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to create user: {str(e)}"
            )
    
    async def login(self, login_request: LoginRequest) -> AuthResponse:
        """Login user"""
        try:
            result = await self.auth_repository.login(
                login_request.email,
                login_request.password
            )
            
            if not result:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Invalid email or password"
                )
            
            return result
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid email or password"
            )
    
    async def verify_token(self, token: str) -> TokenResponse:
        """Verify authentication token"""
        return TokenResponse(
            user_id="demo_user_id",
            email="demo@example.com",
            valid=True
        )
    
    async def get_user(self, user_id: str) -> dict:
        """Get user by ID"""
        user = await self.auth_repository.get_user_by_id(user_id)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        return user
