"""
Champion service - Orchestrates champion operations
"""
from repositories.champion_repository import ChampionRepository
from repositories.player_repository import PlayerRepository
from domain.champion_domain import ChampionDomain
from domain.exceptions import DomainException
from models.champions import (
    ChampionRecommendationRequest,
    ChampionRecommendationResponse,
    ChampionSimilarityRequest,
    ChampionSimilarityResponse,
    ChampionData,
    AbilitySimilarityResponse
)
from fastapi import HTTPException, status
from typing import List
from utils.logger import logger


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
        try:
            self.champion_domain.validate_champion_id(champion_id)
        except DomainException as e:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=e.message)
        
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
        user_id: str,
        request: ChampionRecommendationRequest
    ) -> ChampionRecommendationResponse:
        """Get champion recommendations for player"""
        try:
            self.champion_domain.validate_recommendation_limit(request.limit)
        except DomainException as e:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=e.message)
        
        # Get player's puuid from user_id
        user_summoner = await self.player_repository.get_user_summoner_basic(user_id)
        if not user_summoner:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="No summoner linked to this account"
            )
        
        puuid = user_summoner.get('puuid')
        
        # Get player's champion pool from recent games (last 30 games with EPS/CPS scores)
        champion_pool = await self.champion_repository.get_champion_pool_from_recent_games(puuid, game_limit=30)
        
        logger.info(f"Champion pool from recent games for user {user_id} (puuid: {puuid}): {champion_pool}")

        if not champion_pool:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="No champion data found. Please play some games first and sync your match history to get champion recommendations."
            )
        
        # Get recommendations based on player's recent games champion pool (using puuid)
        # Note: get_similar_champions internally calls get_champion_pool_from_recent_games
        recommendations = await self.champion_repository.get_similar_champions(
            puuid,  # Pass puuid, not champion name
            request.limit
        )
        
        # Rank recommendations
        ranked_recommendations = self.champion_domain.rank_recommendations(
            [rec.dict() for rec in recommendations]
        )
        
        return ChampionRecommendationResponse(
            summoner_id=user_id,
            recommendations=[rec for rec in recommendations],
            based_on_champions=champion_pool
        )
    
    async def calculate_similarity(
        self,
        request: ChampionSimilarityRequest
    ) -> ChampionSimilarityResponse:
        """Calculate similarity between two champions"""
        try:
            self.champion_domain.validate_champion_id(request.champion_a)
            self.champion_domain.validate_champion_id(request.champion_b)
        except DomainException as e:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=e.message)
        
        # Calculate similarity
        similarity_score = await self.champion_repository.calculate_champion_similarity(
            request.champion_a,
            request.champion_b
        )
        
        try:
            self.champion_domain.validate_similarity_score(similarity_score)
        except DomainException as e:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=e.message)
        
        response = ChampionSimilarityResponse(
            champion_a=request.champion_a,
            champion_b=request.champion_b,
            similarity_score=similarity_score
        )
        
        if request.include_details:
            response.ability_similarity = 0.8
            response.stat_similarity = 0.7
            response.playstyle_similarity = 0.75
        
        return response
    
    async def get_ability_similarities(
        self,
        user_id: str,
        champion_id: str,
        limit_per_ability: int = 3
    ) -> AbilitySimilarityResponse:
        """Get ability similarities for a champion filtered by user's champion pool"""
        try:
            self.champion_domain.validate_champion_id(champion_id)
        except DomainException as e:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=e.message)
        
        # Get champion data to verify it exists
        champion = await self.champion_repository.get_champion_by_id(champion_id)
        if not champion:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Champion '{champion_id}' not found"
            )
        
        # Get player's puuid from user_id
        user_summoner = await self.player_repository.get_user_summoner_basic(user_id)
        if not user_summoner:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="No summoner linked to this account"
            )
        
        puuid = user_summoner.get('puuid')
        
        # Get player's champion pool
        champion_pool = await self.champion_repository.get_player_champion_pool(puuid)
        
        logger.info(f"Fetching ability similarities for {champion_id} filtered by champion pool: {champion_pool}")
        
        if not champion_pool:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="No champion data found. Please play some games first and sync your match history."
            )
        
        # Get ability similarities filtered by champion pool
        abilities = await self.champion_repository.get_ability_similarities(
            champion_id,
            limit_per_ability,
            champion_pool
        )
        
        if not abilities:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"No ability similarity data found for champion '{champion_id}' within your champion pool"
            )
        
        return AbilitySimilarityResponse(
            champion_id=champion_id,
            champion_name=champion.name,
            abilities=abilities
        )
