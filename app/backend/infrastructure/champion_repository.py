"""
Champion repository implementation
"""
from repositories.champion_repository import ChampionRepository
from models.champions import ChampionData, ChampionRecommendation, AbilitySimilarity
from infrastructure.database.database_client import DatabaseClient
from typing import Optional, List, Dict, Any
import pandas as pd
from pathlib import Path


class ChampionRepositoryImpl(ChampionRepository):
    """Implementation of champion repository"""
    
    # Class-level cache for ability similarity data
    _ability_data_cache: Optional[pd.DataFrame] = None
    _cache_loaded: bool = False
    
    def __init__(self):
        self._load_ability_data()
    
    def _load_ability_data(self):
        """Load ability similarity data from CSV file into cache"""
        if not ChampionRepositoryImpl._cache_loaded:
            try:
                # Path to the CSV file (in project root output folder)
                pq_path = Path(__file__).resolve().parents[3] / 'data' / 'final_comparisons_20251107_194606.parquet'
                # Load CSV with pandas
                ChampionRepositoryImpl._ability_data_cache = pd.read_parquet(pq_path)
                ChampionRepositoryImpl._cache_loaded = True
                print(f"Loaded ability similarity data: {len(ChampionRepositoryImpl._ability_data_cache)} rows")
            except Exception as e:
                print(f"Error loading ability similarity data: {e}")
                ChampionRepositoryImpl._ability_data_cache = pd.DataFrame()
                ChampionRepositoryImpl._cache_loaded = True
    
    def _normalize_champion_name(self, name: str) -> str:
        """Normalize champion name for comparison (handle special characters, case)"""
        # Remove special characters and spaces, lowercase
        normalized = name.lower().replace("'", "").replace(" ", "").replace(".", "")
        return normalized
    
    async def get_ability_similarities(self, champion_id: str, limit_per_ability: int = 3) -> List[AbilitySimilarity]:
        """Get ability similarities for a champion's Q, W, E, R abilities"""
        if ChampionRepositoryImpl._ability_data_cache is None or ChampionRepositoryImpl._ability_data_cache.empty:
            return []
        
        df = ChampionRepositoryImpl._ability_data_cache
        normalized_champion = self._normalize_champion_name(champion_id)
        
        # Find rows where champ1 matches the requested champion
        # Expected CSV columns: champ1, ability1_type, ability1_name, champ2, ability2_type, ability2_name, score, explanation
        champion_abilities = df[
            df['champ1'].str.lower().str.replace("'", "").str.replace(" ", "").str.replace(".", "") == normalized_champion
        ].copy()
        
        if champion_abilities.empty:
            return []
        
        # Group by ability type and get top similarities for each
        abilities = []
        for ability_type in ['Q', 'W', 'E', 'R']:
            ability_matches = champion_abilities[
                champion_abilities['ability1_type'] == ability_type
            ].nlargest(limit_per_ability, 'score')
            
            for _, row in ability_matches.iterrows():
                abilities.append(AbilitySimilarity(
                    ability_type=row['ability1_type'],
                    ability_name=row['ability1_name'],
                    similar_champion=row['champ2'],
                    similar_ability_type=row['ability2_type'],
                    similar_ability_name=row['ability2_name'],
                    similarity_score=float(row['score']),
                    explanation=row['explanation']
                ))
        
        return abilities

    
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
    
    async def save_champion_data(self, champion_data: dict) -> Optional[ChampionData]:
        """Save champion data to database"""
        # Not implemented for this repository
        return None
    
    async def get_player_champion_pool(self, summoner_id: str) -> List[str]:
        """Get player's most played champions (DEMO)"""
        # Demo implementation
        return ["Ahri", "Lux", "Syndra"]
