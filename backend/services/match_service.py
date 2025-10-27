"""
Match service - Orchestrates match operations
"""
from repositories.match_repository import MatchRepository
from domain.match_domain import MatchDomain
from models.matches import MatchRequest, MatchTimelineResponse, MatchSummaryResponse
from fastapi import HTTPException, status
from typing import Dict, Any


class MatchService:
    """Service for match operations - pure orchestration"""
    
    def __init__(self, match_repository: MatchRepository, match_domain: MatchDomain):
        self.match_repository = match_repository
        self.match_domain = match_domain
    
    async def get_match_timeline(self, match_request: MatchRequest) -> MatchTimelineResponse:
        """Get match timeline"""
        # Validate business rules
        self.match_domain.validate_match_id(match_request.match_id)
        self.match_domain.validate_region(match_request.region)
        
        # Check cache first
        cached = await self.match_repository.get_cached_timeline(match_request.match_id)
        if cached:
            return cached
        
        # Fetch from Riot API
        timeline = await self.match_repository.get_match_timeline(
            match_request.match_id,
            match_request.region
        )
        
        if not timeline:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Match timeline not found"
            )
        
        # Save to cache
        await self.match_repository.save_match_timeline(
            match_request.match_id,
            timeline.dict()
        )
        
        return timeline
    
    async def get_match_summary(self, match_request: MatchRequest) -> MatchSummaryResponse:
        """Get match summary"""
        # Validate business rules
        self.match_domain.validate_match_id(match_request.match_id)
        self.match_domain.validate_region(match_request.region)
        
        # Fetch from Riot API
        summary = await self.match_repository.get_match_summary(
            match_request.match_id,
            match_request.region
        )
        
        if not summary:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Match summary not found"
            )
        
        return summary
    
    async def get_participant_data(self, match_id: str, participant_id: int) -> Dict[str, Any]:
        """Get specific participant data"""
        # Validate
        self.match_domain.validate_match_id(match_id)
        self.match_domain.validate_participant_id(participant_id)
        
        # Get data
        data = await self.match_repository.get_participant_data(match_id, participant_id)
        if not data:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Participant data not found"
            )
        
        return data
