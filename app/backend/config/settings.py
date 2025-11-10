"""
Configuration settings for Rift Rewind API
Loads environment variables and provides app configuration
"""
from pydantic_settings import BaseSettings
from pydantic import field_validator
from typing import Optional, Union


class Settings(BaseSettings):
    """Application settings loaded from environment variables"""
    
    # App Config
    APP_NAME: str = "Rift Rewind API"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = False
    
    # Server Config
    HOST: str = "0.0.0.0"
    PORT: int = 8000
    
    # CORS - can be set as comma-separated string in env or list
    ALLOWED_ORIGINS: Union[str, list[str]] = ["http://localhost:3000", "http://localhost:5173"]
    
    @field_validator('ALLOWED_ORIGINS', mode='before')
    @classmethod
    def parse_cors_origins(cls, v):
        """Parse CORS origins from string or list"""
        if isinstance(v, str):
            # Split by comma and strip whitespace
            return [origin.strip() for origin in v.split(',') if origin.strip()]
        return v
    
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
    AWS_BEDROCK_MODEL: str = "us.anthropic.claude-sonnet-4-5-20250929-v1:0"
    
    # OpenRouter API
    OPENROUTER_API_KEY: Optional[str] = None
    
    class Config:
        env_file = ".env"
        case_sensitive = True


# Global settings instance
settings = Settings()
