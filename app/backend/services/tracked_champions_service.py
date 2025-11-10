"""
Tracked Champions Service
Orchestrates tracked champions operations
"""
from fastapi import HTTPException, status
from repositories.tracked_champions_repository import TrackedChampionsRepository
from domain.tracked_champions_domain import (
    TrackedChampionsDomain,
    MaxTrackedChampionsError,
    ChampionAlreadyTrackedError,
    ChampionNotTrackedError
)
from domain.exceptions import ValidationError
from models.tracked_champions import (
    TrackedChampionsResponse,
    TrackChampionResponse,
    TrackChampionRequest,
    UntrackChampionRequest
)


class TrackedChampionsService:
    """Service for managing tracked champions"""
    
    def __init__(
        self,
        repository: TrackedChampionsRepository,
        domain: TrackedChampionsDomain
    ):
        """
        Initialize service with repository and domain
        
        Args:
            repository: Tracked champions repository
            domain: Tracked champions domain logic
        """
        self.repository = repository
        self.domain = domain
    
    async def get_tracked_champions(self, user_id: str) -> TrackedChampionsResponse:
        """
        Get user's tracked champions
        
        Args:
            user_id: User's UUID
            
        Returns:
            TrackedChampionsResponse with list of tracked champions
            
        Raises:
            HTTPException: If retrieval fails
        """
        tracked_champions = await self.repository.get_tracked_champions(user_id)
        
        if tracked_champions is None:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to retrieve tracked champions"
            )
        
        return TrackedChampionsResponse(
            tracked_champions=tracked_champions,
            count=len(tracked_champions),
            max_allowed=self.domain.MAX_TRACKED_CHAMPIONS
        )
    
    async def track_champion(
        self,
        user_id: str,
        request: TrackChampionRequest
    ) -> TrackChampionResponse:
        """
        Add a champion to user's tracked list
        
        Args:
            user_id: User's UUID
            request: Track champion request
            
        Returns:
            TrackChampionResponse with tracked champion data
            
        Raises:
            HTTPException: If validation fails or tracking fails
        """
        champion_id = request.champion_id
        
        # Validate champion ID
        try:
            self.domain.validate_champion_id(champion_id)
        except ValidationError as e:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=e.message
            )
        
        # Get current tracked champions
        tracked_champions = await self.repository.get_tracked_champions(user_id)
        if tracked_champions is None:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to check tracked champions"
            )
        
        tracked_ids = [tc.champion_id for tc in tracked_champions]
        
        # Validate tracking limit
        try:
            self.domain.validate_tracking_limit(len(tracked_champions))
        except MaxTrackedChampionsError as e:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=e.message
            )
        
        # Validate not already tracked
        try:
            self.domain.validate_not_already_tracked(champion_id, tracked_ids)
        except ChampionAlreadyTrackedError as e:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=e.message
            )
        
        # Add to tracked list
        result = await self.repository.add_tracked_champion(user_id, champion_id)
        if not result:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to track champion"
            )
        
        return TrackChampionResponse(
            message="Champion tracked successfully",
            champion_id=result.champion_id,
            tracked_at=result.tracked_at
        )
    
    async def untrack_champion(
        self,
        user_id: str,
        request: UntrackChampionRequest
    ) -> dict:
        """
        Remove a champion from user's tracked list
        
        Args:
            user_id: User's UUID
            request: Untrack champion request
            
        Returns:
            Success message
            
        Raises:
            HTTPException: If validation fails or removal fails
        """
        champion_id = request.champion_id
        
        # Validate champion ID
        try:
            self.domain.validate_champion_id(champion_id)
        except ValidationError as e:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=e.message
            )
        
        # Get current tracked champions
        tracked_champions = await self.repository.get_tracked_champions(user_id)
        if tracked_champions is None:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to check tracked champions"
            )
        
        tracked_ids = [tc.champion_id for tc in tracked_champions]
        
        # Validate is tracked
        try:
            self.domain.validate_is_tracked(champion_id, tracked_ids)
        except ChampionNotTrackedError as e:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=e.message
            )
        
        # Remove from tracked list
        result = await self.repository.remove_tracked_champion(user_id, champion_id)
        if result is None:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to untrack champion"
            )
        
        if not result:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Champion not found in tracked list"
            )
        
        return {"message": "Champion removed from tracking successfully"}
