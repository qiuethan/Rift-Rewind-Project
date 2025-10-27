"""
Auth service - Orchestrates authentication operations
"""
from repositories.auth_repository import AuthRepository
from domain.auth_domain import AuthDomain
from models.auth import RegisterRequest, LoginRequest, AuthResponse, TokenResponse
from fastapi import HTTPException, status


class AuthService:
    """Service for authentication - pure orchestration"""
    
    def __init__(self, auth_repository: AuthRepository, auth_domain: AuthDomain):
        self.auth_repository = auth_repository
        self.auth_domain = auth_domain
    
    async def register(self, register_request: RegisterRequest) -> AuthResponse:
        """Register a new user"""
        # Validate business rules
        self.auth_domain.validate_email(register_request.email)
        self.auth_domain.validate_password(register_request.password)
        
        if register_request.summoner_name:
            self.auth_domain.validate_summoner_name(register_request.summoner_name)
        
        if register_request.region:
            self.auth_domain.validate_region(register_request.region)
        
        # Check if user already exists
        existing_user = await self.auth_repository.get_user_by_email(register_request.email)
        if existing_user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="User with this email already exists"
            )
        
        # Create user
        user_data = {
            'summoner_name': register_request.summoner_name,
            'region': register_request.region
        }
        
        return await self.auth_repository.create_user(
            register_request.email,
            register_request.password,
            user_data
        )
    
    async def login(self, login_request: LoginRequest) -> AuthResponse:
        """Login user"""
        # Validate credentials
        is_valid = await self.auth_repository.verify_password(
            login_request.email,
            login_request.password
        )
        
        if not is_valid:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid email or password"
            )
        
        # Get user data
        user = await self.auth_repository.get_user_by_email(login_request.email)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid email or password"
            )
        
        # Generate token (demo)
        import secrets
        token = secrets.token_urlsafe(32)
        
        return AuthResponse(
            user_id=user['id'],
            email=user['email'],
            token=token,
            summoner_name=user.get('summoner_name'),
            region=user.get('region')
        )
    
    async def verify_token(self, token: str) -> TokenResponse:
        """Verify authentication token"""
        # Demo implementation - would verify JWT
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
