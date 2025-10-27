"""
Auth repository interface - Abstract contract for auth data access
"""
from abc import ABC, abstractmethod
from typing import Optional
from models.auth import AuthResponse


class AuthRepository(ABC):
    """Abstract interface for authentication data access"""
    
    @abstractmethod
    async def create_user(self, email: str, password: str, user_data: dict) -> AuthResponse:
        """Create a new user"""
        pass
    
    @abstractmethod
    async def get_user_by_email(self, email: str) -> Optional[dict]:
        """Get user by email"""
        pass
    
    @abstractmethod
    async def get_user_by_id(self, user_id: str) -> Optional[dict]:
        """Get user by ID"""
        pass
    
    @abstractmethod
    async def verify_password(self, email: str, password: str) -> bool:
        """Verify user password"""
        pass
    
    @abstractmethod
    async def update_user(self, user_id: str, user_data: dict) -> dict:
        """Update user data"""
        pass
