"""
Champion domain - Pure business logic for champion operations
"""
from fastapi import HTTPException, status
from typing import List


class ChampionDomain:
    """Pure business logic for champion operations"""
    
    def __init__(self):
        pass
    
    def validate_champion_id(self, champion_id: str) -> None:
        """Validate champion ID format"""
        if not champion_id or len(champion_id) < 2:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid champion ID"
            )
    
    def validate_similarity_score(self, score: float) -> None:
        """Validate similarity score is between 0 and 1"""
        if score < 0.0 or score > 1.0:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Similarity score must be between 0 and 1"
            )
    
    def validate_recommendation_limit(self, limit: int) -> None:
        """Validate recommendation limit"""
        if limit < 1 or limit > 20:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Recommendation limit must be between 1 and 20"
            )
    
    def calculate_ability_similarity(self, abilities_a: List[str], abilities_b: List[str]) -> float:
        """
        Calculate similarity between two sets of abilities
        This is a placeholder - actual implementation would use LLM
        """
        # Simple Jaccard similarity for demo
        set_a = set(abilities_a)
        set_b = set(abilities_b)
        
        if not set_a or not set_b:
            return 0.0
        
        intersection = len(set_a.intersection(set_b))
        union = len(set_a.union(set_b))
        
        return round(intersection / union, 2) if union > 0 else 0.0
    
    def calculate_stat_similarity(self, stats_a: dict, stats_b: dict) -> float:
        """
        Calculate similarity between champion stats
        This is a placeholder - actual implementation would use proper distance metrics
        """
        # Simple normalized difference for demo
        common_stats = set(stats_a.keys()).intersection(set(stats_b.keys()))
        
        if not common_stats:
            return 0.0
        
        differences = []
        for stat in common_stats:
            val_a = stats_a.get(stat, 0)
            val_b = stats_b.get(stat, 0)
            
            # Normalize difference
            max_val = max(abs(val_a), abs(val_b), 1)
            diff = abs(val_a - val_b) / max_val
            differences.append(1 - diff)
        
        return round(sum(differences) / len(differences), 2)
    
    def rank_recommendations(self, recommendations: List[dict]) -> List[dict]:
        """Rank recommendations by similarity score"""
        return sorted(recommendations, key=lambda x: x.get('similarity_score', 0), reverse=True)
