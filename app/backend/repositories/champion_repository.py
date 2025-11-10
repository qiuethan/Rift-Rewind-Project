"""
Champion repository interface - Abstract contract for champion data access
"""
from abc import ABC, abstractmethod
from typing import Optional, List, Dict, Any
from models.champions import ChampionData, ChampionRecommendation, AbilitySimilarity


class ChampionRepository(ABC):
    """Abstract interface for champion data access"""
    
    @abstractmethod
    async def get_champion_by_id(self, champion_id: str) -> Optional[ChampionData]:
        """Get champion data by ID"""
        pass
    
    @abstractmethod
    async def get_all_champions(self) -> List[ChampionData]:
        """Get all champion data"""
        pass
    
    @abstractmethod
    async def get_champion_abilities(self, champion_id: str) -> List[Dict[str, Any]]:
        """Get champion abilities"""
        pass
    
    @abstractmethod
    async def calculate_champion_similarity(self, champion_a: str, champion_b: str) -> float:
        """Calculate similarity between two champions"""
        pass
    
    @abstractmethod
    async def get_similar_champions(self, champion_id: str, limit: int) -> List[ChampionRecommendation]:
        """Get similar champions"""
        pass
    
    @abstractmethod
    async def save_champion_data(self, champion_data: dict) -> Optional[ChampionData]:
        """Save champion data to database, or None if failed"""
        pass
    
    @abstractmethod
    async def get_player_champion_pool(self, summoner_id: str) -> List[str]:
        """Get player's most played champions"""
        pass
    
    @abstractmethod
    async def get_ability_similarities(self, champion_id: str, limit_per_ability: int = 3) -> List[AbilitySimilarity]:
        """Get ability similarities for a champion's Q, W, E, R abilities"""
        pass
