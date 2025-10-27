"""
Auth repository Supabase implementation
"""
from repositories.auth_repository import AuthRepository
from models.auth import AuthResponse
from fastapi import HTTPException, status
from typing import Optional
import hashlib
import secrets


class AuthRepositorySupabase(AuthRepository):
    """Supabase implementation of auth repository"""
    
    def __init__(self, client):
        self.client = client
    
    async def create_user(self, email: str, password: str, user_data: dict) -> AuthResponse:
        """Create a new user in Supabase"""
        try:
            # Create user with Supabase Auth
            if self.client:
                auth_response = self.client.auth.sign_up({
                    "email": email,
                    "password": password
                })
                
                user_id = auth_response.user.id
                token = auth_response.session.access_token
                
                # Insert additional user data into users table
                self.client.table('users').insert({
                    'id': user_id,
                    'email': email,
                    **user_data
                }).execute()
            else:
                # Demo mode
                user_id = f"demo_user_{secrets.token_hex(8)}"
                token = secrets.token_urlsafe(32)
            
            return AuthResponse(
                user_id=user_id,
                email=email,
                token=token,
                summoner_name=user_data.get('summoner_name'),
                region=user_data.get('region')
            )
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to create user: {str(e)}"
            )
    
    async def get_user_by_email(self, email: str) -> Optional[dict]:
        """Get user by email from Supabase"""
        try:
            if self.client:
                response = self.client.table('users').select('*').eq('email', email).limit(1).execute()
                if response.data:
                    return response.data[0]
            return None
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to get user: {str(e)}"
            )
    
    async def get_user_by_id(self, user_id: str) -> Optional[dict]:
        """Get user by ID from Supabase"""
        try:
            if self.client:
                response = self.client.table('users').select('*').eq('id', user_id).limit(1).execute()
                if response.data:
                    return response.data[0]
            return None
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to get user: {str(e)}"
            )
    
    async def verify_password(self, email: str, password: str) -> bool:
        """Verify user password with Supabase Auth"""
        try:
            if self.client:
                # Use Supabase Auth to verify password
                auth_response = self.client.auth.sign_in_with_password({
                    "email": email,
                    "password": password
                })
                return auth_response.user is not None
            else:
                # Demo mode - simple hash check
                user = await self.get_user_by_email(email)
                if not user:
                    return False
                password_hash = hashlib.sha256(password.encode()).hexdigest()
                return user.get('password_hash') == password_hash
        except Exception:
            return False
    
    async def update_user(self, user_id: str, user_data: dict) -> dict:
        """Update user data in Supabase"""
        try:
            if self.client:
                response = self.client.table('users').update(user_data).eq('id', user_id).execute()
                if response.data:
                    return response.data[0]
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to update user: {str(e)}"
            )
