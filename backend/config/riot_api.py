"""
Riot API Configuration
"""
from config.settings import settings
import httpx
from typing import Optional, Dict, Any
from utils.logger import logger


class RiotAPIConfig:
    """Configuration and client for Riot API"""
    
    # Region mapping: routing regions to platform regions
    REGION_MAP = {
        'americas': 'na1',
        'europe': 'euw1',
        'asia': 'kr',
        'sea': 'oc1'
    }
    
    # Valid platform regions
    PLATFORM_REGIONS = ['NA1', 'BR1', 'LA1', 'LA2', 'EUW1', 'EUN1', 'TR1', 'RU', 'KR', 'JP1', 'OC1']
    
    # Base URLs
    ACCOUNT_API_BASE = "https://{region}.api.riotgames.com"
    SUMMONER_API_BASE = "https://{region}.api.riotgames.com"
    LEAGUE_API_BASE = "https://{region}.api.riotgames.com"
    MASTERY_API_BASE = "https://{region}.api.riotgames.com"
    
    def __init__(self, api_key: str):
        """Initialize Riot API configuration"""
        if not api_key:
            logger.error("CRITICAL: Riot API key not provided")
            raise ValueError("Riot API key is required")
        
        self.api_key = api_key.strip()
        self.headers = {
            "X-Riot-Token": self.api_key,
            "Accept": "application/json"
        }
        logger.info("Riot API configuration initialized")
    
    def get_platform_region(self, region: str) -> str:
        """Convert routing region to platform region"""
        if region.upper() in self.PLATFORM_REGIONS:
            return region.lower()
        return self.REGION_MAP.get(region.lower(), 'na1')
    
    async def request(self, url: str, error_context: str = "Riot API") -> Optional[Dict[Any, Any]]:
        """Make HTTP request to Riot API with proper error handling"""
        try:
            logger.debug(f"Calling {error_context}: {url}")
            
            async with httpx.AsyncClient() as client:
                response = await client.get(url, headers=self.headers, timeout=10.0)
                
                if response.status_code == 200:
                    return response.json()
                elif response.status_code == 404:
                    logger.warning(f"{error_context} - Not found: {url}")
                    return None
                elif response.status_code == 429:
                    logger.error(f"{error_context} - Rate limit exceeded")
                    return None
                elif response.status_code == 403:
                    logger.error(f"{error_context} - Forbidden (check API key)")
                    return None
                else:
                    logger.error(f"{error_context} error: {response.status_code} - {response.text}")
                    return None
                    
        except httpx.TimeoutException:
            logger.error(f"{error_context} - Request timeout")
            return None
        except Exception as e:
            logger.error(f"{error_context} - Error: {str(e)}")
            return None


# Singleton instance
riot_api_config = RiotAPIConfig(settings.RIOT_API_KEY) if settings.RIOT_API_KEY else None
