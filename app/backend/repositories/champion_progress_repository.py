"""
Champion Progress Repository Interface - Abstract contract for data access
Following Clean Architecture: Define contracts, not implementations
"""
from abc import ABC, abstractmethod
from typing import Optional, List
from models.champion_progress import (
    ChampionProgressResponse,
    AllChampionsProgressResponse,
    ChampionProgressRecord,
    UpdateChampionProgressRequest
)


class ChampionProgressRepository(ABC):
    """Abstract interface for champion progress data access"""
    
    @abstractmethod
    async def get_champion_progress(
        self, 
        user_id: str, 
        champion_id: int, 
        limit: int
    ) -> Optional[ChampionProgressResponse]:
        """
        Get progress data for a specific champion
        
        Args:
            user_id: User ID
            champion_id: Champion ID
            limit: Number of recent matches to include
            
        Returns:
            ChampionProgressResponse or None if not found
        """
        pass
    
    @abstractmethod
    async def get_all_champions_progress(
        self, 
        user_id: str
    ) -> Optional[AllChampionsProgressResponse]:
        """
        Get progress data for all champions played by user
        
        Args:
            user_id: User ID
            
        Returns:
            AllChampionsProgressResponse or None if no data
        """
        pass
    
    @abstractmethod
    async def update_champion_progress(
        self,
        user_id: str,
        puuid: str,
        update_request: UpdateChampionProgressRequest
    ) -> Optional[ChampionProgressRecord]:
        """
        Update champion progress after a match
        
        Args:
            user_id: User ID
            puuid: Player PUUID
            update_request: Match data to update progress
            
        Returns:
            Updated ChampionProgressRecord or None if failed
        """
        pass
    
    @abstractmethod
    async def get_champion_progress_record(
        self,
        user_id: str,
        champion_id: int
    ) -> Optional[ChampionProgressRecord]:
        """
        Get raw champion progress record from database
        
        Args:
            user_id: User ID
            champion_id: Champion ID
            
        Returns:
            ChampionProgressRecord or None if not found
        """
        pass
    
    @abstractmethod
    async def create_champion_progress_record(
        self,
        record: ChampionProgressRecord
    ) -> Optional[ChampionProgressRecord]:
        """
        Create a new champion progress record
        
        Args:
            record: ChampionProgressRecord to create
            
        Returns:
            Created record or None if failed
        """
        pass
    
    @abstractmethod
    async def delete_champion_progress(
        self,
        user_id: str,
        champion_id: Optional[int] = None
    ) -> bool:
        """
        Delete champion progress data
        
        Args:
            user_id: User ID
            champion_id: Specific champion ID, or None to delete all
            
        Returns:
            True if successful, False otherwise
        """
        pass
