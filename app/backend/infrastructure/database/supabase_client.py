"""
Supabase implementation of database client with async support
"""
from infrastructure.database.database_client import (
    DatabaseClient, TableQuery, QueryResponse, AuthResponse, AuthUser, AuthSession
)
from typing import Optional, Dict, Any
import asyncio


class SupabaseTableQuery(TableQuery):
    """Supabase implementation of table query"""
    
    def __init__(self, supabase_table):
        self._query = supabase_table
    
    def select(self, columns: str = '*') -> 'SupabaseTableQuery':
        self._query = self._query.select(columns)
        return self
    
    def insert(self, data: Dict[str, Any]) -> 'SupabaseTableQuery':
        self._query = self._query.insert(data)
        return self
    
    def upsert(self, data: Dict[str, Any]) -> 'SupabaseTableQuery':
        self._query = self._query.upsert(data)
        return self
    
    def update(self, data: Dict[str, Any]) -> 'SupabaseTableQuery':
        self._query = self._query.update(data)
        return self
    
    def delete(self) -> 'SupabaseTableQuery':
        self._query = self._query.delete()
        return self
    
    def eq(self, column: str, value: Any) -> 'SupabaseTableQuery':
        self._query = self._query.eq(column, value)
        return self
    
    def limit(self, count: int) -> 'SupabaseTableQuery':
        self._query = self._query.limit(count)
        return self
    
    def contains(self, column: str, value: Any) -> 'SupabaseTableQuery':
        """Filter rows where column contains value (for JSONB arrays)"""
        self._query = self._query.contains(column, value)
        return self
    
    def order(self, column: str, desc: bool = False) -> 'SupabaseTableQuery':
        """Order results by column"""
        self._query = self._query.order(column, desc=desc)
        return self
    
    async def execute(self) -> QueryResponse:
        """Execute query asynchronously to prevent blocking"""
        result = await asyncio.to_thread(self._query.execute)
        return QueryResponse(data=result.data if hasattr(result, 'data') else [])


class SupabaseClient(DatabaseClient):
    """Supabase implementation of database client"""
    
    def __init__(self, supabase_client):
        self._client = supabase_client
    
    def table(self, table_name: str) -> SupabaseTableQuery:
        return SupabaseTableQuery(self._client.table(table_name))
    
    async def auth_sign_up(self, email: str, password: str) -> AuthResponse:
        """Sign up user asynchronously"""
        response = await asyncio.to_thread(
            self._client.auth.sign_up,
            {"email": email, "password": password}
        )
        return AuthResponse(
            user=AuthUser(id=response.user.id, email=response.user.email),
            session=AuthSession(access_token=response.session.access_token)
        )
    
    async def auth_sign_in(self, email: str, password: str) -> AuthResponse:
        """Sign in user asynchronously"""
        response = await asyncio.to_thread(
            self._client.auth.sign_in_with_password,
            {"email": email, "password": password}
        )
        return AuthResponse(
            user=AuthUser(id=response.user.id, email=response.user.email),
            session=AuthSession(access_token=response.session.access_token)
        )
    
    async def auth_get_user(self, token: str) -> AuthUser:
        """Get user by token asynchronously"""
        response = await asyncio.to_thread(self._client.auth.get_user, token)
        return AuthUser(id=response.user.id, email=response.user.email)
