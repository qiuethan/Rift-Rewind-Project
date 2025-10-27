"""
Supabase initialization and configuration
Provides Supabase client setup
"""
from supabase import create_client, Client
from config.settings import settings
from typing import Optional


class SupabaseService:
    """Singleton service for Supabase operations"""
    
    _instance: Optional['SupabaseService'] = None
    _initialized: bool = False
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
    
    def __init__(self):
        if not self._initialized:
            self._initialize_supabase()
            self._initialized = True
    
    def _initialize_supabase(self):
        """Initialize Supabase client"""
        try:
            if settings.SUPABASE_URL and settings.SUPABASE_KEY:
                # Create client with positional arguments (compatible with v2.3.0)
                self.client: Client = create_client(
                    settings.SUPABASE_URL,
                    settings.SUPABASE_KEY
                )
                print(f"✅ Supabase client initialized: {settings.SUPABASE_URL}")
            else:
                print("⚠️  Warning: Supabase credentials not found. Using demo mode.")
                self.client = None
            
        except Exception as e:
            print(f"❌ Warning: Supabase initialization failed: {e}")
            # For demo purposes, set to None
            self.client = None
    
    def verify_token(self, token: str) -> dict:
        """Verify JWT token"""
        if not self.client:
            raise Exception("Supabase client not initialized")
        
        user = self.client.auth.get_user(token)
        return user


# Global Supabase service instance
supabase_service = SupabaseService()
