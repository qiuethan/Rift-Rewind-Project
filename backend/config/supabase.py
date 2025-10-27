"""
Supabase initialization and configuration
Provides Supabase configuration and client initialization
"""
from supabase import create_client
from config.settings import settings
from infrastructure.database.supabase_client import SupabaseClient
from infrastructure.database.database_client import DatabaseClient
from typing import Optional
import logging

logger = logging.getLogger(__name__)

# Initialize database client
supabase_service: Optional[DatabaseClient] = None

if settings.SUPABASE_URL and settings.SUPABASE_KEY:
    try:
        raw_client = create_client(settings.SUPABASE_URL, settings.SUPABASE_KEY)
        supabase_service = SupabaseClient(raw_client)
        logger.info(f"Supabase client initialized: {settings.SUPABASE_URL}")
    except Exception as e:
        logger.error(f"Failed to initialize Supabase client: {e}")
        supabase_service = None
else:
    logger.warning("Supabase credentials not configured")
    supabase_service = None
