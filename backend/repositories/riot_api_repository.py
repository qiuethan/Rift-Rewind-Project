"""
Riot API Repository Interface - Abstract contract for Riot API operations
"""
from abc import ABC, abstractmethod
from typing import Optional, List, Dict, Any


class RiotAPIRepository(ABC):
    """Abstract interface for Riot API data access"""
    
    # ============================================================================
    # ACCOUNT API
    # ============================================================================
    
    @abstractmethod
    async def get_account_by_riot_id(self, game_name: str, tag_line: str, region: str) -> Optional[Dict[str, Any]]:
        """
        Get account by Riot ID (game_name#tag_line)
        Returns: {puuid, gameName, tagLine}
        """
        pass
    
    # ============================================================================
    # SUMMONER API
    # ============================================================================
    
    @abstractmethod
    async def get_summoner_by_puuid(self, puuid: str, region: str) -> Optional[Dict[str, Any]]:
        """
        Get summoner by PUUID
        Returns: {id, accountId, puuid, name, profileIconId, summonerLevel}
        """
        pass
    
    # ============================================================================
    # LEAGUE API (Ranked)
    # ============================================================================
    
    @abstractmethod
    async def get_league_entries_by_summoner(self, summoner_id: str, region: str) -> List[Dict[str, Any]]:
        """
        Get ranked league entries for summoner by encrypted summoner ID
        Returns: List of {queueType, tier, rank, leaguePoints, wins, losses}
        """
        pass
    
    @abstractmethod
    async def get_league_entries_by_puuid(self, puuid: str, region: str) -> List[Dict[str, Any]]:
        """
        Get ranked league entries for summoner by PUUID
        Returns: List of {queueType, tier, rank, leaguePoints, wins, losses}
        """
        pass
    
    # ============================================================================
    # CHAMPION MASTERY API
    # ============================================================================
    
    @abstractmethod
    async def get_champion_masteries(self, puuid: str, region: str) -> List[Dict[str, Any]]:
        """
        Get all champion masteries for summoner
        Returns: List of mastery objects
        """
        pass
    
    @abstractmethod
    async def get_top_champion_masteries(self, puuid: str, region: str, count: int) -> List[Dict[str, Any]]:
        """
        Get top N champion masteries for summoner
        Returns: List of top mastery objects
        """
        pass
    
    @abstractmethod
    async def get_mastery_score(self, puuid: str, region: str) -> int:
        """Get total mastery score for summoner"""
        pass
    
    @abstractmethod
    async def get_champion_mastery_by_champion(self, puuid: str, champion_id: int, region: str) -> Optional[Dict[str, Any]]:
        """
        Get mastery for specific champion
        Returns: Mastery object for the champion
        """
        pass
    
    # ============================================================================
    # MATCH API v5
    # ============================================================================
    
    @abstractmethod
    async def get_match_ids_by_puuid(self, puuid: str, region: str, count: int = 10) -> List[str]:
        """Get list of match IDs for a player"""
        pass
    
    @abstractmethod
    async def get_match_details(self, match_id: str, region: str) -> Optional[Dict[str, Any]]:
        """Get detailed match data by match ID"""
        pass
