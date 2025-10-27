"""
Player service - Orchestrates player operations
"""
from repositories.player_repository import PlayerRepository
from domain.player_domain import PlayerDomain
from models.players import SummonerRequest, SummonerResponse, PlayerStatsResponse
from fastapi import HTTPException, status
from typing import List
from utils.logger import logger


class PlayerService:
    """Service for player operations - pure orchestration"""
    
    def __init__(self, player_repository: PlayerRepository, player_domain: PlayerDomain):
        self.player_repository = player_repository
        self.player_domain = player_domain
    
    async def link_summoner(self, user_id: str, summoner_request: SummonerRequest) -> SummonerResponse:
        """Link summoner account to user"""
        # Validate region
        self.player_domain.validate_region(summoner_request.region)
        
        # Debug logging
        logger.debug(f"Received request - game_name: '{summoner_request.game_name}', tag_line: '{summoner_request.tag_line}', summoner_name: '{summoner_request.summoner_name}'")
        
        # Check if using Riot ID (game_name + tag_line) or old format (summoner_name)
        has_riot_id = summoner_request.game_name and summoner_request.tag_line and \
                      summoner_request.game_name.strip() and summoner_request.tag_line.strip()
        has_summoner_name = summoner_request.summoner_name and summoner_request.summoner_name.strip()
        
        logger.debug(f"Validation check - has_riot_id: {has_riot_id}, has_summoner_name: {has_summoner_name}")
        logger.debug(f"game_name type: {type(summoner_request.game_name)}, value: '{summoner_request.game_name}'")
        logger.debug(f"tag_line type: {type(summoner_request.tag_line)}, value: '{summoner_request.tag_line}'")
        
        if has_riot_id:
            # New Riot ID format
            summoner = await self.player_repository.get_summoner_by_riot_id(
                summoner_request.game_name.strip(),
                summoner_request.tag_line.strip(),
                summoner_request.region
            )
        elif has_summoner_name:
            # Old format (legacy)
            self.player_domain.validate_summoner_name(summoner_request.summoner_name)
            summoner = await self.player_repository.get_summoner_by_name(
                summoner_request.summoner_name.strip(),
                summoner_request.region
            )
        else:
            logger.error(f"Validation failed - game_name: '{summoner_request.game_name}', tag_line: '{summoner_request.tag_line}', summoner_name: '{summoner_request.summoner_name}'")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Must provide either game_name+tag_line or summoner_name"
            )
        
        if not summoner:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Summoner not found"
            )
        
        # Save to database
        summoner_data = summoner.dict()
        # Ensure game_name and tag_line are set from request
        if summoner_request.game_name:
            summoner_data['game_name'] = summoner_request.game_name
        if summoner_request.tag_line:
            summoner_data['tag_line'] = summoner_request.tag_line
        
        logger.debug(f"Saving summoner data: {summoner_data}")
        result = await self.player_repository.save_summoner(user_id, summoner_data)
        
        if not result:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to save summoner"
            )
        
        return result
    
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
