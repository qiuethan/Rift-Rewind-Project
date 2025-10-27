"""
Player repository interface - Abstract contract for player data access
"""
from abc import ABC, abstractmethod
from typing import Optional, List
from models.players import SummonerResponse, PlayerStatsResponse


class PlayerRepository(ABC):
    """Abstract interface for player data access"""
    
    @abstractmethod
    async def get_summoner_by_name(self, summoner_name: str, region: str) -> Optional[SummonerResponse]:
        """Get summoner data by name from Riot API"""
        pass
    
    @abstractmethod
    async def get_summoner_by_puuid(self, puuid: str) -> Optional[SummonerResponse]:
        """Get summoner data by PUUID from Riot API"""
        pass
    
    @abstractmethod
    async def save_summoner(self, user_id: str, summoner_data: dict) -> SummonerResponse:
        """Save summoner data to database"""
        pass
    
    @abstractmethod
    async def get_user_summoner(self, user_id: str) -> Optional[SummonerResponse]:
        """Get user's linked summoner from database"""
        pass
    
    @abstractmethod
    async def get_player_stats(self, summoner_id: str) -> Optional[PlayerStatsResponse]:
        """Get player statistics"""
        pass
    
    @abstractmethod
    async def get_match_history(self, puuid: str, count: int) -> List[str]:
        """Get match history for a player"""
        pass
