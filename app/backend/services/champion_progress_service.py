"""
Champion Progress Service - Business logic orchestration
Following Clean Architecture: Coordinates domain + repositories, converts exceptions
"""
from repositories.champion_progress_repository import ChampionProgressRepository
from repositories.player_repository import PlayerRepository
from domain.champion_progress_domain import ChampionProgressDomain
from domain.exceptions import DomainException
from models.champion_progress import (
    ChampionProgressRequest,
    ChampionProgressResponse,
    AllChampionsProgressResponse,
    UpdateChampionProgressRequest
)
from fastapi import HTTPException, status
from utils.logger import logger


class ChampionProgressService:
    """Service for champion progress operations"""
    
    def __init__(
        self,
        champion_progress_repository: ChampionProgressRepository,
        player_repository: PlayerRepository,
        champion_progress_domain: ChampionProgressDomain
    ):
        """
        Initialize service with injected dependencies
        
        Args:
            champion_progress_repository: Repository for champion progress data
            player_repository: Repository for player data
            champion_progress_domain: Domain logic for validation
        """
        self.champion_progress_repository = champion_progress_repository
        self.player_repository = player_repository
        self.champion_progress_domain = champion_progress_domain
        logger.info("Champion progress service initialized")
    
    async def get_champion_progress(
        self,
        user_id: str,
        request: ChampionProgressRequest
    ) -> ChampionProgressResponse:
        """
        Get progress data for a specific champion
        
        Args:
            user_id: User ID
            request: Champion progress request
            
        Returns:
            ChampionProgressResponse
            
        Raises:
            HTTPException: If validation fails or data not found
        """
        logger.info(f"Getting champion progress for user {user_id}, champion {request.champion_id}")
        
        # Validate with domain
        try:
            if request.champion_id:
                self.champion_progress_domain.validate_champion_id(request.champion_id)
            self.champion_progress_domain.validate_limit(request.limit)
        except DomainException as e:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=e.message)
        
        # Get data from repository
        result = await self.champion_progress_repository.get_champion_progress(
            user_id,
            request.champion_id,
            request.limit
        )
        
        if not result:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"No progress data found for champion {request.champion_id}"
            )
        
        logger.info(f"Successfully retrieved champion progress")
        return result
    
    async def get_all_champions_progress(
        self,
        user_id: str
    ) -> AllChampionsProgressResponse:
        """
        Get progress data for all champions
        
        Args:
            user_id: User ID
            
        Returns:
            AllChampionsProgressResponse
            
        Raises:
            HTTPException: If no data found
        """
        logger.info(f"Getting all champions progress for user {user_id}")
        
        result = await self.champion_progress_repository.get_all_champions_progress(user_id)
        
        if not result:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="No champion progress data found"
            )
        
        logger.info(f"Successfully retrieved progress for {result.total_champions_played} champions")
        return result
    
    async def update_champion_progress_from_match(
        self,
        user_id: str,
        update_request: UpdateChampionProgressRequest
    ) -> ChampionProgressResponse:
        """
        Update champion progress after a match
        
        Args:
            user_id: User ID
            update_request: Match data to update progress
            
        Returns:
            Updated ChampionProgressResponse
            
        Raises:
            HTTPException: If validation fails or update fails
        """
        logger.info(f"Updating champion progress for user {user_id}, champion {update_request.champion_id}")
        
        # Validate with domain
        try:
            self.champion_progress_domain.validate_champion_id(update_request.champion_id)
            self.champion_progress_domain.validate_score(update_request.eps_score, "EPS score")
            self.champion_progress_domain.validate_score(update_request.cps_score, "CPS score")
            self.champion_progress_domain.validate_kda_components(
                update_request.kills,
                update_request.deaths,
                update_request.assists
            )
        except DomainException as e:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=e.message)
        
        # Get user's PUUID
        user_summoner = await self.player_repository.get_user_summoner_basic(user_id)
        if not user_summoner:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="No summoner linked to this account"
            )
        
        puuid = user_summoner.get('puuid')
        region = user_summoner.get('region', 'americas')
        
        # Fetch current mastery data for this champion
        mastery_level = None
        mastery_points = None
        try:
            mastery_data = await self.player_repository.get_champion_mastery_by_champion(
                puuid,
                update_request.champion_id,
                region
            )
            if mastery_data:
                mastery_level = mastery_data.champion_level
                mastery_points = mastery_data.champion_points
                logger.info(f"Fetched mastery for champion {update_request.champion_id}: Level {mastery_level}, {mastery_points} points")
        except Exception as e:
            logger.warning(f"Could not fetch mastery data for champion {update_request.champion_id}: {e}")
        
        # Update progress with mastery data
        result = await self.champion_progress_repository.update_champion_progress(
            user_id,
            puuid,
            update_request,
            mastery_level,
            mastery_points
        )
        
        if not result:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to update champion progress"
            )
        
        # Fetch and return updated progress
        progress_request = ChampionProgressRequest(
            champion_id=update_request.champion_id,
            limit=10
        )
        
        return await self.get_champion_progress(user_id, progress_request)
    
    async def delete_champion_progress(
        self,
        user_id: str,
        champion_id: int = None
    ) -> dict:
        """
        Delete champion progress data
        
        Args:
            user_id: User ID
            champion_id: Specific champion ID, or None to delete all
            
        Returns:
            Success message
            
        Raises:
            HTTPException: If deletion fails
        """
        logger.info(f"Deleting champion progress for user {user_id}, champion {champion_id}")
        
        # Validate champion_id if provided
        if champion_id is not None:
            try:
                self.champion_progress_domain.validate_champion_id(champion_id)
            except DomainException as e:
                raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=e.message)
        
        success = await self.champion_progress_repository.delete_champion_progress(
            user_id,
            champion_id
        )
        
        if not success:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to delete champion progress"
            )
        
        message = f"Deleted progress for champion {champion_id}" if champion_id else "Deleted all champion progress"
        logger.info(message)
        return {"message": message}
