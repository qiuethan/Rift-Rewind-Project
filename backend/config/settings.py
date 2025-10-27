"""
Configuration settings for Rift Rewind API
Loads environment variables and provides app configuration
"""
from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    """Application settings loaded from environment variables"""
    
    # App Config
    APP_NAME: str = "Rift Rewind API"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = False
    
    # Server Config
    HOST: str = "0.0.0.0"
    PORT: int = 8000
    
    # CORS
    ALLOWED_ORIGINS: list[str] = ["http://localhost:3000", "http://localhost:5173"]
    
    # Supabase
    SUPABASE_URL: Optional[str] = None
    SUPABASE_KEY: Optional[str] = None
    
    # Riot API
    RIOT_API_KEY: Optional[str] = None
    RIOT_API_BASE_URL: str = "https://americas.api.riotgames.com"
    
    # AWS Bedrock
    AWS_ACCESS_KEY_ID: Optional[str] = None
    AWS_SECRET_ACCESS_KEY: Optional[str] = None
    AWS_REGION: str = "us-east-1"
    AWS_BEDROCK_MODEL: str = "anthropic.claude-3-5-sonnet-20241022-v2:0"
    
    class Config:
        env_file = ".env"
        case_sensitive = True


# Global settings instance
settings = Settings()
