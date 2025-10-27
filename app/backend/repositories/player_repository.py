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
    async def get_summoner_by_riot_id(self, game_name: str, tag_line: str, region: str) -> Optional[SummonerResponse]:
        """Get summoner data by Riot ID (game_name#tag_line) from Riot API"""
        pass
    
    @abstractmethod
    async def get_summoner_by_puuid(self, puuid: str) -> Optional[SummonerResponse]:
        """Get summoner data by PUUID from Riot API"""
        pass
    
    @abstractmethod
    async def save_summoner(self, user_id: str, summoner_data: dict) -> Optional[SummonerResponse]:
        """Save summoner data to database, or None if failed"""
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
    async def get_match_history(self, puuid: str, count: int) -> 'MatchHistoryResponse':
        """Get match history for a player"""
        pass
    
    @abstractmethod
    async def get_ranked_data(self, summoner_id: str, region: str) -> 'RankedData':
        """Get ranked data for a summoner (solo/flex tier, rank, LP, wins, losses)"""
        pass
    
    @abstractmethod
    async def get_mastery_data(self, puuid: str, region: str) -> 'MasteryData':
        """Get champion mastery data (all masteries, top champions, total score)"""
        pass
    
    @abstractmethod
    async def get_champion_masteries(self, puuid: str, region: str) -> List['ChampionMasteryResponse']:
        """Get all champion masteries for a summoner"""
        pass
    
    @abstractmethod
    async def get_top_champion_masteries(self, puuid: str, region: str, count: int) -> List['ChampionMasteryResponse']:
        """Get top N champion masteries for a summoner"""
        pass
    
    @abstractmethod
    async def get_mastery_score(self, puuid: str, region: str) -> Optional[int]:
        """Get total mastery score for a summoner"""
        pass
    
    @abstractmethod
    async def get_champion_mastery_by_champion(self, puuid: str, champion_id: int, region: str) -> Optional['ChampionMasteryResponse']:
        """Get mastery data for a specific champion"""
        pass
    
    @abstractmethod
    async def get_recent_games(self, puuid: str, region: str, count: int = 5) -> List[dict]:
        """Get recent games for a player"""
        pass
    
    @abstractmethod
    async def get_user_summoner_basic(self, user_id: str) -> Optional[dict]:
        """Get basic user summoner info (PUUID and region) without fetching fresh data"""
        pass
