"""
Database client interface - Abstract contract for database operations
"""
from abc import ABC, abstractmethod
from typing import Optional, List, Dict, Any


class DatabaseClient(ABC):
    """Abstract interface for database operations"""
    
    @abstractmethod
    def table(self, table_name: str) -> 'TableQuery':
        """Get a table query builder"""
        pass
    
    @abstractmethod
    def auth_sign_up(self, email: str, password: str) -> 'AuthResponse':
        """Sign up a new user"""
        pass
    
    @abstractmethod
    def auth_sign_in(self, email: str, password: str) -> 'AuthResponse':
        """Sign in a user"""
        pass
    
    @abstractmethod
    def auth_get_user(self, token: str) -> 'AuthUser':
        """Get user from token"""
        pass


class TableQuery(ABC):
    """Abstract interface for table query operations"""
    
    @abstractmethod
    def select(self, columns: str = '*') -> 'TableQuery':
        """Select columns"""
        pass
    
    @abstractmethod
    def insert(self, data: Dict[str, Any]) -> 'TableQuery':
        """Insert data"""
        pass
    
    @abstractmethod
    def upsert(self, data: Dict[str, Any]) -> 'TableQuery':
        """Upsert data"""
        pass
    
    @abstractmethod
    def update(self, data: Dict[str, Any]) -> 'TableQuery':
        """Update data"""
        pass
    
    @abstractmethod
    def delete(self) -> 'TableQuery':
        """Delete data"""
        pass
    
    @abstractmethod
    def eq(self, column: str, value: Any) -> 'TableQuery':
        """Filter by equality"""
        pass
    
    @abstractmethod
    def limit(self, count: int) -> 'TableQuery':
        """Limit results"""
        pass
    
    @abstractmethod
    def execute(self) -> 'QueryResponse':
        """Execute the query"""
        pass


class QueryResponse:
    """Response from a database query"""
    def __init__(self, data: Optional[List[Dict[str, Any]]] = None):
        self.data = data or []


class AuthResponse:
    """Response from auth operations"""
    def __init__(self, user: 'AuthUser', session: 'AuthSession'):
        self.user = user
        self.session = session


class AuthUser:
    """User from auth"""
    def __init__(self, id: str, email: str):
        self.id = id
        self.email = email


class AuthSession:
    """Session from auth"""
    def __init__(self, access_token: str):
        self.access_token = access_token
