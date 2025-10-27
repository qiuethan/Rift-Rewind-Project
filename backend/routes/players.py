"""
Player routes
"""
from fastapi import APIRouter, status, Depends
from models.players import SummonerRequest, SummonerResponse, PlayerStatsResponse
from services.player_service import PlayerService
from dependency.dependencies import get_player_service
from middleware.auth import get_current_user
from typing import List
from utils.logger import logger


router = APIRouter(prefix="/api/players", tags=["players"])


@router.post("/summoner", response_model=SummonerResponse, status_code=status.HTTP_201_CREATED)
async def link_summoner(
    summoner_request: SummonerRequest,
    current_user: str = Depends(get_current_user),
    player_service: PlayerService = Depends(get_player_service)
):
    """Link summoner account to user"""
    logger.info(f"POST /api/players/summoner - User: {current_user}")
    logger.debug(f"Request body: {summoner_request.dict()}")
    logger.info(f"About to call player_service.link_summoner")
    result = await player_service.link_summoner(current_user, summoner_request)
    logger.info(f"Successfully linked summoner")
    return result


@router.get("/summoner", response_model=SummonerResponse)
async def get_summoner(
    current_user: str = Depends(get_current_user),
    player_service: PlayerService = Depends(get_player_service)
):
    """Get user's linked summoner"""
    logger.info(f"GET /api/players/summoner - User: {current_user}")
    return await player_service.get_summoner(current_user)


@router.get("/stats/{summoner_id}", response_model=PlayerStatsResponse)
async def get_player_stats(
    summoner_id: str,
    player_service: PlayerService = Depends(get_player_service)
):
    """Get player statistics (public endpoint)"""
    return await player_service.get_player_stats(summoner_id)


@router.get("/matches", response_model=List[str])
async def get_match_history(
    count: int = 20,
    current_user: str = Depends(get_current_user),
    player_service: PlayerService = Depends(get_player_service)
):
    """Get player's match history"""
    return await player_service.get_match_history(current_user, count)
