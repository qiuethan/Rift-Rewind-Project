"""
Champion repository implementation with Supabase and LLM
"""
from repositories.champion_repository import ChampionRepository
from models.champions import ChampionData, ChampionRecommendation
from fastapi import HTTPException, status
from typing import Optional, List, Dict, Any


class ChampionRepositorySupabase(ChampionRepository):
    """Supabase + LLM implementation of champion repository"""
    
    def __init__(self, client, openrouter_api_key: Optional[str] = None):
        self.client = client
        self.openrouter_api_key = openrouter_api_key
    
    async def get_champion_by_id(self, champion_id: str) -> Optional[ChampionData]:
        """Get champion data by ID (DEMO)"""
        # Demo implementation - would query from database
        return ChampionData(
            id=champion_id,
            name=champion_id.capitalize(),
            title="The Demo Champion",
            tags=["Mage", "Assassin"],
            stats={"hp": 500, "attack": 60, "armor": 30},
            abilities=[]
        )
    
    async def get_all_champions(self) -> List[ChampionData]:
        """Get all champion data (DEMO)"""
        # Demo implementation
        demo_champions = ["Ahri", "Lux", "Syndra", "Zed", "Yasuo"]
        return [
            ChampionData(
                id=champ.lower(),
                name=champ,
                title=f"The {champ}",
                tags=["Mage"],
                stats={},
                abilities=[]
            )
            for champ in demo_champions
        ]
    
    async def get_champion_abilities(self, champion_id: str) -> List[Dict[str, Any]]:
        """Get champion abilities (DEMO)"""
        # Demo implementation
        return [
            {"name": "Q - Demo Ability", "description": "Demo description"},
            {"name": "W - Demo Ability", "description": "Demo description"},
            {"name": "E - Demo Ability", "description": "Demo description"},
            {"name": "R - Demo Ultimate", "description": "Demo description"}
        ]
    
    async def calculate_champion_similarity(self, champion_a: str, champion_b: str) -> float:
        """Calculate similarity between two champions using LLM (DEMO)"""
        # Demo implementation - would use LLM API
        return 0.75
    
    async def get_similar_champions(self, champion_id: str, limit: int) -> List[ChampionRecommendation]:
        """Get similar champions (DEMO)"""
        # Demo implementation
        similar = ["Ahri", "Syndra", "Orianna", "Viktor", "Cassiopeia"]
        return [
            ChampionRecommendation(
                champion_id=champ.lower(),
                champion_name=champ,
                similarity_score=0.8 - (i * 0.1),
                reasoning=f"{champ} has similar playstyle and abilities",
                similar_abilities=["Q", "W"],
                playstyle_match="Control Mage"
            )
            for i, champ in enumerate(similar[:limit])
        ]
    
    async def save_champion_data(self, champion_data: dict) -> ChampionData:
        """Save champion data to Supabase"""
        try:
            if self.client:
                self.client.table('champions').upsert(champion_data).execute()
            return ChampionData(**champion_data)
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to save champion: {str(e)}"
            )
    
    async def get_player_champion_pool(self, summoner_id: str) -> List[str]:
        """Get player's most played champions (DEMO)"""
        # Demo implementation
        return ["Ahri", "Lux", "Syndra"]
