"""
Match repository interface - Abstract contract for match data access
"""
from abc import ABC, abstractmethod
from typing import Optional, Dict, Any, List
from models.matches import MatchTimelineResponse, MatchSummaryResponse


class MatchRepository(ABC):
    """Abstract interface for match data access"""
    
    @abstractmethod
    async def get_match_timeline(self, match_id: str, region: str) -> Optional[MatchTimelineResponse]:
        """Get match timeline from Riot API"""
        pass
    
    @abstractmethod
    async def get_match_summary(self, match_id: str, region: str) -> Optional[MatchSummaryResponse]:
        """Get match summary from Riot API"""
        pass
    
    @abstractmethod
    async def save_match_timeline(self, match_id: str, timeline_data: dict) -> Optional[MatchTimelineResponse]:
        """Save match timeline to database, or None if failed"""
        pass
    
    @abstractmethod
    async def get_cached_timeline(self, match_id: str) -> Optional[MatchTimelineResponse]:
        """Get cached match timeline from database"""
        pass
    
    @abstractmethod
    async def get_participant_data(self, match_id: str, participant_id: int) -> Optional[Dict[str, Any]]:
        """Get specific participant data from match"""
        pass
    
    @abstractmethod
    async def save_match(
        self, 
        match_id: str, 
        match_data: Dict[str, Any],
        puuid: str = None,
        timeline_data: Dict[str, Any] = None,
        mastery_level: Optional[int] = None,
        mastery_points: Optional[int] = None
    ) -> bool:
        """
        Save complete match data to database
        
        Args:
            match_id: Match ID
            match_data: Full match data from Riot API
            puuid: Optional PUUID of summoner to track
            timeline_data: Optional timeline data
            mastery_level: Optional mastery level for champion progress
            mastery_points: Optional mastery points for champion progress
            
        Returns:
            True if successful, False otherwise
        """
        pass
    
    @abstractmethod
    async def get_match(self, match_id: str) -> Optional[Dict[str, Any]]:
        """
        Get complete match data from database
        
        Args:
            match_id: Unique match identifier
            
        Returns:
            Complete match data or None if not found
        """
        pass
    
    @abstractmethod
    async def match_exists(self, match_id: str) -> bool:
        """
        Check if a match already exists in database
        
        Args:
            match_id: Unique match identifier
            
        Returns:
            True if match exists, False otherwise
        """
        pass
    
    @abstractmethod
    async def get_player_matches(self, puuid: str, limit: int = 20) -> List[Dict[str, Any]]:
        """
        Get all matches for a specific player
        
        Args:
            puuid: Player's PUUID
            limit: Maximum number of matches to return
            
        Returns:
            List of match data dictionaries
        """
        pass
    
    @abstractmethod
    async def sync_player_matches(self, puuid: str, region: str, riot_api, max_matches: int = 100) -> int:
        """
        Sync matches for a player from Riot API to database.
        Fetches new matches and stops when hitting existing ones or reaching max_matches.
        
        Args:
            puuid: Player's PUUID
            region: Regional routing value
            riot_api: RiotAPIRepository instance for fetching data
            max_matches: Maximum number of matches to sync (default 100)
            
        Returns:
            Number of new matches saved
        """
        pass
    
    @abstractmethod
    async def is_match_history_synced(self, puuid: str, region: str, riot_api) -> bool:
        """
        Check if player's match history is already synced.
        
        Args:
            puuid: Player's PUUID
            region: Regional routing value
            riot_api: RiotAPIRepository instance
            
        Returns:
            True if synced (first match exists), False otherwise
        """
        pass
