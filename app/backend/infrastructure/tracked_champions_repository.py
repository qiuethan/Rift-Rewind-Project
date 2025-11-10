"""
Tracked Champions Repository Implementation
Supabase implementation for tracked champions data access
"""
from typing import Optional, List
from repositories.tracked_champions_repository import TrackedChampionsRepository
from models.tracked_champions import TrackedChampion
from infrastructure.database.database_client import DatabaseClient
from utils.logger import logger


class TrackedChampionsRepositorySupabase(TrackedChampionsRepository):
    """Supabase implementation of tracked champions repository"""
    
    def __init__(self, db: DatabaseClient):
        """
        Initialize repository with database client
        
        Args:
            db: Database abstraction for data persistence
        """
        self.db = db
    
    async def get_tracked_champions(self, user_id: str) -> Optional[List[TrackedChampion]]:
        """Get all tracked champions for a user"""
        try:
            response = await self.db.table('tracked_champions')\
                .select('champion_id, tracked_at')\
                .eq('user_id', user_id)\
                .order('tracked_at', desc=False)\
                .execute()
            
            if not response or not hasattr(response, 'data'):
                return []
            
            return [TrackedChampion(**item) for item in response.data]
        except Exception as e:
            logger.error(f"Error getting tracked champions: {str(e)}")
            return None
    
    async def add_tracked_champion(self, user_id: str, champion_id: int) -> Optional[TrackedChampion]:
        """Add a champion to user's tracked list"""
        try:
            response = await self.db.table('tracked_champions')\
                .insert({
                    'user_id': user_id,
                    'champion_id': champion_id
                })\
                .execute()
            
            if not response or not hasattr(response, 'data') or not response.data:
                return None
            
            return TrackedChampion(**response.data[0])
        except Exception as e:
            logger.error(f"Error adding tracked champion: {str(e)}")
            return None
    
    async def remove_tracked_champion(self, user_id: str, champion_id: int) -> Optional[bool]:
        """Remove a champion from user's tracked list"""
        try:
            response = await self.db.table('tracked_champions')\
                .delete()\
                .eq('user_id', user_id)\
                .eq('champion_id', champion_id)\
                .execute()
            
            if not response or not hasattr(response, 'data'):
                return None
            
            # Return True if something was deleted
            return len(response.data) > 0 if response.data else False
        except Exception as e:
            logger.error(f"Error removing tracked champion: {str(e)}")
            return None
    
    async def get_tracked_count(self, user_id: str) -> Optional[int]:
        """Get count of tracked champions for a user"""
        try:
            response = await self.db.table('tracked_champions')\
                .select('id', count='exact')\
                .eq('user_id', user_id)\
                .execute()
            
            if not response or not hasattr(response, 'count'):
                return 0
            
            return response.count
        except Exception as e:
            logger.error(f"Error getting tracked count: {str(e)}")
            return None
