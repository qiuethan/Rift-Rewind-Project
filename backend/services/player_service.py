"""
Player service - Orchestrates player operations
"""
from repositories.player_repository import PlayerRepository
from domain.player_domain import PlayerDomain
from models.players import SummonerRequest, SummonerResponse, PlayerStatsResponse
from fastapi import HTTPException, status
from typing import List


class PlayerService:
    """Service for player operations - pure orchestration"""
    
    def __init__(self, player_repository: PlayerRepository, player_domain: PlayerDomain):
        self.player_repository = player_repository
        self.player_domain = player_domain
    
    async def link_summoner(self, user_id: str, summoner_request: SummonerRequest) -> SummonerResponse:
        """Link summoner account to user"""
        # Validate business rules
        self.player_domain.validate_summoner_name(summoner_request.summoner_name)
        self.player_domain.validate_region(summoner_request.region)
        
        # Get summoner data from Riot API
        summoner = await self.player_repository.get_summoner_by_name(
            summoner_request.summoner_name,
            summoner_request.region
        )
        
        if not summoner:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Summoner not found"
            )
        
        # Save to database
        summoner_data = summoner.dict()
        return await self.player_repository.save_summoner(user_id, summoner_data)
    
    async def get_summoner(self, user_id: str) -> SummonerResponse:
        """Get user's linked summoner"""
        summoner = await self.player_repository.get_user_summoner(user_id)
        if not summoner:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="No summoner linked to this account"
            )
        return summoner
    
    async def get_player_stats(self, summoner_id: str) -> PlayerStatsResponse:
        """Get player statistics"""
        stats = await self.player_repository.get_player_stats(summoner_id)
        if not stats:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Player stats not found"
            )
        return stats
    
    async def get_match_history(self, user_id: str, count: int = 20) -> List[str]:
        """Get player's match history"""
        # Get summoner
        summoner = await self.get_summoner(user_id)
        
        # Validate PUUID
        self.player_domain.validate_puuid(summoner.puuid)
        
        # Get match history
        return await self.player_repository.get_match_history(summoner.puuid, count)
