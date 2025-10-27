"""
Match repository interface - Abstract contract for match data access
"""
from abc import ABC, abstractmethod
from typing import Optional, Dict, Any
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
