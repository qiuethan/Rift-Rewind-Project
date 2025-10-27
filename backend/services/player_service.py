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
        self.player_domain.validate_region(summoner_request.region)
        
        logger.debug(f"Received request - game_name: '{summoner_request.game_name}', tag_line: '{summoner_request.tag_line}', summoner_name: '{summoner_request.summoner_name}'")
        
        has_riot_id = summoner_request.game_name and summoner_request.tag_line and \
                      summoner_request.game_name.strip() and summoner_request.tag_line.strip()
        has_summoner_name = summoner_request.summoner_name and summoner_request.summoner_name.strip()
        
        logger.debug(f"Validation check - has_riot_id: {has_riot_id}, has_summoner_name: {has_summoner_name}")
        
        if has_riot_id:
            summoner = await self.player_repository.get_summoner_by_riot_id(
                summoner_request.game_name.strip(),
                summoner_request.tag_line.strip(),
                summoner_request.region
            )
        elif has_summoner_name:
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
        
        logger.info(f"Fetching ranked and mastery data for summoner: {summoner.puuid}")
        
        # Use PUUID for ranked data since encrypted summoner ID is not available
        ranked_data = await self.player_repository.get_ranked_data_by_puuid(summoner.puuid, summoner_request.region)
        logger.info(f"Ranked data fetched: {ranked_data.dict()}")
        
        mastery_data = await self.player_repository.get_mastery_data(summoner.puuid, summoner_request.region)
        logger.info(f"Mastery data fetched: {len(mastery_data.champion_masteries)} masteries")
        
        summoner_data = summoner.dict()
        logger.debug(f"Base summoner data: {summoner_data}")
        
        summoner_data.update(ranked_data.dict())
        logger.debug(f"After ranked update: ranked_solo_tier={summoner_data.get('ranked_solo_tier')}")
        
        summoner_data.update(mastery_data.to_dict())  # Use to_dict() for proper JSONB conversion
        logger.debug(f"After mastery update: champion_masteries count={len(summoner_data.get('champion_masteries', []))}")
        
        # Ensure game_name and tag_line are set
        if summoner_request.game_name:
            summoner_data['game_name'] = summoner_request.game_name
        if summoner_request.tag_line:
            summoner_data['tag_line'] = summoner_request.tag_line
        
        logger.debug(f"Saving complete summoner data to database: {summoner_data.keys()}")
        result = await self.player_repository.save_summoner(user_id, summoner_data)
        
        if not result:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to save summoner"
            )
        
        return result
    
    async def get_summoner(self, user_id: str) -> SummonerResponse:
        """Get user's linked summoner with fresh data"""
        summoner = await self.player_repository.get_user_summoner(user_id)
        
        if not summoner:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="No summoner linked to this account"
            )
        
        logger.info(f"Fetching fresh data for summoner: {summoner.puuid} in region: {summoner.region}")
        
        try:
            # Get fresh summoner data with ranked and mastery
            fresh_summoner = await self.player_repository.get_summoner_by_puuid(summoner.puuid, summoner.region)
            
            if fresh_summoner:
                logger.info(f"Successfully fetched fresh data - Masteries: {len(fresh_summoner.champion_masteries) if fresh_summoner.champion_masteries else 0}")
                logger.debug(f"Top champions: {len(fresh_summoner.top_champions) if fresh_summoner.top_champions else 0}")
                return fresh_summoner
            
            logger.warning("get_summoner_by_puuid returned None")
        except Exception as e:
            logger.error(f"Error fetching fresh summoner data: {str(e)}", exc_info=True)
        
        # Fallback to DB data if API fails
        logger.warning("Failed to fetch fresh data, returning cached data from DB")
        
        # Ensure top_champions is computed from DB data
        if summoner.champion_masteries and not summoner.top_champions:
            summoner.top_champions = summoner.champion_masteries[:10]
            logger.info(f"Computed top_champions from DB: {len(summoner.top_champions)}")
        
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
