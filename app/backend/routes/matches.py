"""
Match routes
"""
from fastapi import APIRouter, status, Depends, Query
from models.matches import MatchRequest, MatchTimelineResponse, MatchSummaryResponse
from services.match_service import MatchService
from dependency.dependencies import get_match_service
from typing import Dict, Any


router = APIRouter(prefix="/api/matches", tags=["matches"])


@router.get("/{match_id}/timeline", response_model=MatchTimelineResponse)
async def get_match_timeline(
    match_id: str,
    region: str = Query("americas", pattern="^(americas|asia|europe|sea)$"),
    match_service: MatchService = Depends(get_match_service)
):
    """Get match timeline (public endpoint)"""
    match_request = MatchRequest(match_id=match_id, region=region)
    return await match_service.get_match_timeline(match_request)


@router.get("/{match_id}/summary", response_model=MatchSummaryResponse)
async def get_match_summary(
    match_id: str,
    region: str = Query("americas", pattern="^(americas|asia|europe|sea)$"),
    match_service: MatchService = Depends(get_match_service)
):
    """Get match summary (public endpoint)"""
    match_request = MatchRequest(match_id=match_id, region=region)
    return await match_service.get_match_summary(match_request)


@router.get("/{match_id}/participant/{participant_id}", response_model=Dict[str, Any])
async def get_participant_data(
    match_id: str,
    participant_id: int,
    match_service: MatchService = Depends(get_match_service)
):
    """Get specific participant data from match (public endpoint)"""
    return await match_service.get_participant_data(match_id, participant_id)
