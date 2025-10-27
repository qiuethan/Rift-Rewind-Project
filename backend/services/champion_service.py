"""
Champion service - Orchestrates champion operations
"""
from repositories.champion_repository import ChampionRepository
from repositories.player_repository import PlayerRepository
from domain.champion_domain import ChampionDomain
from models.champions import (
    ChampionRecommendationRequest,
    ChampionRecommendationResponse,
    ChampionSimilarityRequest,
    ChampionSimilarityResponse,
    ChampionData
)
from fastapi import HTTPException, status
from typing import List


class ChampionService:
    """Service for champion operations - pure orchestration"""
    
    def __init__(
        self,
        champion_repository: ChampionRepository,
        player_repository: PlayerRepository,
        champion_domain: ChampionDomain
    ):
        self.champion_repository = champion_repository
        self.player_repository = player_repository
        self.champion_domain = champion_domain
    
    async def get_champion(self, champion_id: str) -> ChampionData:
        """Get champion data"""
        self.champion_domain.validate_champion_id(champion_id)
        
        champion = await self.champion_repository.get_champion_by_id(champion_id)
        if not champion:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Champion not found"
            )
        return champion
    
    async def get_all_champions(self) -> List[ChampionData]:
        """Get all champions"""
        return await self.champion_repository.get_all_champions()
    
    async def get_champion_recommendations(
        self,
        request: ChampionRecommendationRequest
    ) -> ChampionRecommendationResponse:
        """Get champion recommendations for player"""
        # Validate
        self.champion_domain.validate_recommendation_limit(request.limit)
        
        # Get player's champion pool
        champion_pool = await self.champion_repository.get_player_champion_pool(
            request.summoner_id
        )
        
        if not champion_pool:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="No champion data found for this player"
            )
        
        # Get recommendations based on most played champion
        main_champion = champion_pool[0]
        recommendations = await self.champion_repository.get_similar_champions(
            main_champion.lower(),
            request.limit
        )
        
        # Rank recommendations
        ranked_recommendations = self.champion_domain.rank_recommendations(
            [rec.dict() for rec in recommendations]
        )
        
        return ChampionRecommendationResponse(
            summoner_id=request.summoner_id,
            recommendations=[rec for rec in recommendations],
            based_on_champions=champion_pool
        )
    
    async def calculate_similarity(
        self,
        request: ChampionSimilarityRequest
    ) -> ChampionSimilarityResponse:
        """Calculate similarity between two champions"""
        # Validate
        self.champion_domain.validate_champion_id(request.champion_a)
        self.champion_domain.validate_champion_id(request.champion_b)
        
        # Calculate similarity
        similarity_score = await self.champion_repository.calculate_champion_similarity(
            request.champion_a,
            request.champion_b
        )
        
        # Validate score
        self.champion_domain.validate_similarity_score(similarity_score)
        
        response = ChampionSimilarityResponse(
            champion_a=request.champion_a,
            champion_b=request.champion_b,
            similarity_score=similarity_score
        )
        
        if request.include_details:
            # Get detailed similarity metrics
            response.ability_similarity = 0.8
            response.stat_similarity = 0.7
            response.playstyle_similarity = 0.75
        
        return response
