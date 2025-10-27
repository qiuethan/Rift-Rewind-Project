"""
Auth repository Supabase implementation
"""
from repositories.auth_repository import AuthRepository
from models.auth import AuthResponse
from infrastructure.database.database_client import DatabaseClient
from constants.database import DatabaseTable
from typing import Optional


class AuthRepositorySupabase(AuthRepository):
    """Supabase implementation of auth repository"""
    
    def __init__(self, client: DatabaseClient):
        self.client = client
    
    async def create_user(self, email: str, password: str, user_data: dict) -> Optional[AuthResponse]:
        """Create a new user"""
        if self.client:
            auth_response = self.client.auth_sign_up(email, password)
            
            user_id = auth_response.user.id
            token = auth_response.session.access_token
            
            self.client.table(DatabaseTable.USERS).insert({
                'id': user_id,
                'email': email,
                **user_data
            }).execute()
            
            return AuthResponse(
                user_id=user_id,
                email=email,
                token=token,
                summoner_name=user_data.get('summoner_name'),
                region=user_data.get('region')
            )
        return None
    
    async def get_user_by_email(self, email: str) -> Optional[dict]:
        """Get user by email from Supabase"""
        if self.client:
            response = self.client.table(DatabaseTable.USERS).select('*').eq('email', email).limit(1).execute()
            if response.data:
                return response.data[0]
        return None
    
    async def get_user_by_id(self, user_id: str) -> Optional[dict]:
        """Get user by ID from Supabase"""
        if self.client:
            response = self.client.table(DatabaseTable.USERS).select('*').eq('id', user_id).limit(1).execute()
            if response.data:
                return response.data[0]
        return None
    
    async def verify_password(self, email: str, password: str) -> bool:
        """Verify user password"""
        if self.client:
            auth_response = self.client.auth_sign_in(email, password)
            return auth_response.user is not None
        return False
    
    async def login(self, email: str, password: str) -> Optional[AuthResponse]:
        """Login user and return auth response with token"""
        if self.client:
            auth_response = self.client.auth_sign_in(email, password)
            user_data = await self.get_user_by_id(auth_response.user.id)
            
            return AuthResponse(
                user_id=auth_response.user.id,
                email=auth_response.user.email,
                token=auth_response.session.access_token,
                summoner_name=user_data.get('summoner_name') if user_data else None,
                region=user_data.get('region') if user_data else None
            )
        return None
    
    async def update_user(self, user_id: str, user_data: dict) -> Optional[dict]:
        """Update user data in Supabase"""
        if self.client:
            response = self.client.table(DatabaseTable.USERS).update(user_data).eq('id', user_id).execute()
            if response.data:
                return response.data[0]
        return None
