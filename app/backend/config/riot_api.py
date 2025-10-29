"""
Riot API Configuration with built-in rate limiting
"""
from config.settings import settings
import httpx
import asyncio
from typing import Optional, Dict, Any
from collections import deque
from datetime import datetime, timedelta
from utils.logger import logger


class RateLimiter:
    """Token bucket rate limiter for Riot API with concurrent request support"""
    
    def __init__(self, requests_per_second: int = 20, requests_per_two_minutes: int = 200):
        """
        Initialize rate limiter with token buckets
        
        Args:
            requests_per_second: Maximum requests per second (default 20)
            requests_per_two_minutes: Maximum requests per 2 minutes (default 200)
        """
        self.requests_per_second = requests_per_second
        self.requests_per_two_minutes = requests_per_two_minutes
        
        # Semaphore to limit concurrent requests
        self.semaphore = asyncio.Semaphore(requests_per_second)
        
        # Timestamps for 2-minute window
        self.request_timestamps: deque = deque()
        
        # Last refill time for per-second bucket
        self.last_second_refill = datetime.now()
        self.second_bucket = float(requests_per_second)
        
        # Lock only for timestamp management
        self.lock = asyncio.Lock()
        
        logger.info(f"Rate limiter initialized: {requests_per_second} req/s, {requests_per_two_minutes} req/2min")
    
    async def _cleanup_old_timestamps(self):
        """Remove timestamps older than 2 minutes"""
        now = datetime.now()
        two_minutes_ago = now - timedelta(minutes=2)
        
        async with self.lock:
            while self.request_timestamps and self.request_timestamps[0] < two_minutes_ago:
                self.request_timestamps.popleft()
    
    async def _wait_for_two_min_window(self):
        """Wait if we've hit the 2-minute limit"""
        while True:
            await self._cleanup_old_timestamps()
            
            async with self.lock:
                if len(self.request_timestamps) < self.requests_per_two_minutes:
                    self.request_timestamps.append(datetime.now())
                    return
            
            # Wait a bit before checking again
            await asyncio.sleep(0.1)
    
    async def acquire(self):
        """
        Acquire permission to make a request with concurrent support
        Uses semaphore for per-second limit and deque for 2-minute window
        """
        # Check 2-minute window first
        await self._wait_for_two_min_window()
        
        # Acquire semaphore for per-second rate limit
        # This allows up to N concurrent requests per second
        await self.semaphore.acquire()
        
        # Release after 1 second to refill the bucket
        asyncio.create_task(self._release_after_delay())
        
        logger.debug(f"Rate limit: {len(self.request_timestamps)} requests in 2min window")
    
    async def _release_after_delay(self):
        """Release semaphore after 1 second to maintain per-second rate"""
        await asyncio.sleep(1.0 / self.requests_per_second)
        self.semaphore.release()


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
    MATCH_API_BASE = "https://{region}.api.riotgames.com"
    
    def __init__(self, api_key: str, requests_per_second: float = 20, requests_per_two_minutes: int = 100):
        """Initialize Riot API configuration with rate limiting"""
        if not api_key:
            logger.error("CRITICAL: Riot API key not provided")
            raise ValueError("Riot API key is required")
        
        self.api_key = api_key.strip()
        self.headers = {
            "X-Riot-Token": self.api_key,
            "Accept": "application/json"
        }
        
        # Initialize rate limiter
        self.rate_limiter = RateLimiter(requests_per_second, requests_per_two_minutes)
        logger.info("Riot API configuration initialized with rate limiting")
    
    def get_platform_region(self, region: str) -> str:
        """Convert routing region to platform region"""
        if region.upper() in self.PLATFORM_REGIONS:
            return region.lower()
        return self.REGION_MAP.get(region.lower(), 'na1')
    
    async def request(self, url: str, error_context: str = "Riot API") -> Optional[Dict[Any, Any]]:
        """
        Make HTTP request to Riot API with automatic rate limiting
        Non-blocking - will queue and wait if rate limit is reached
        """
        # Wait for rate limiter permission (non-blocking)
        await self.rate_limiter.acquire()
        
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
                    # Rate limit hit despite our limiter - back off more
                    logger.error(f"{error_context} - Rate limit exceeded (429 response)")
                    retry_after = response.headers.get('Retry-After', '1')
                    logger.info(f"Backing off for {retry_after} seconds")
                    await asyncio.sleep(float(retry_after))
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
