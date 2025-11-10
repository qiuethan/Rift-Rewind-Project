"""
Tracked Champions Repository Interface
Defines contract for tracked champions data access
"""
from abc import ABC, abstractmethod
from typing import Optional, List
from models.tracked_champions import TrackedChampion


class TrackedChampionsRepository(ABC):
    """Abstract repository for tracked champions operations"""
    
    @abstractmethod
    async def get_tracked_champions(self, user_id: str) -> Optional[List[TrackedChampion]]:
        """
        Get all tracked champions for a user
        
        Args:
            user_id: User's UUID
            
        Returns:
            List of tracked champions or None if error
        """
        pass
    
    @abstractmethod
    async def add_tracked_champion(self, user_id: str, champion_id: int) -> Optional[TrackedChampion]:
        """
        Add a champion to user's tracked list
        
        Args:
            user_id: User's UUID
            champion_id: Champion ID to track
            
        Returns:
            Tracked champion data or None if error
        """
        pass
    
    @abstractmethod
    async def remove_tracked_champion(self, user_id: str, champion_id: int) -> Optional[bool]:
        """
        Remove a champion from user's tracked list
        
        Args:
            user_id: User's UUID
            champion_id: Champion ID to untrack
            
        Returns:
            True if removed, None if error or not found
        """
        pass
    
    @abstractmethod
    async def get_tracked_count(self, user_id: str) -> Optional[int]:
        """
        Get count of tracked champions for a user
        
        Args:
            user_id: User's UUID
            
        Returns:
            Count of tracked champions or None if error
        """
        pass
