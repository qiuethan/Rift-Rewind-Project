"""
Context Repository - Abstract interface for retrieving LLM context
Clean Architecture - Layer 3 (Repository Interface)
"""
from abc import ABC, abstractmethod
from typing import Optional, Dict, Any


class ContextRepository(ABC):
    """Abstract repository for retrieving context data for LLM"""
    
    @abstractmethod
    async def get_summoner_context(self, puuid: str) -> Optional[Dict[str, Any]]:
        """
        Retrieve basic summoner info
        
        Args:
            puuid: Player UUID
            
        Returns:
            Dict with game_name and region, or None if not found
        """
        pass
    
    @abstractmethod
    async def get_champion_progress_context(self, puuid: str, champion_id: int) -> Optional[Dict[str, Any]]:
        """
        Retrieve champion progress data
        
        Args:
            puuid: Player UUID
            champion_id: Champion ID
            
        Returns:
            Dict with champion progress stats, or None if not found
        """
        pass
    
    @abstractmethod
    async def get_match_context(self, puuid: str, match_id: str) -> Optional[Dict[str, Any]]:
        """
        Retrieve match information
        
        Args:
            puuid: Player UUID
            match_id: Match ID
            
        Returns:
            Dict with match info (game_type, player's champion, analysis), or None if not found
        """
        pass
