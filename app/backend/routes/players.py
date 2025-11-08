"""
Player routes
"""
from fastapi import APIRouter, status, Depends, Query
from fastapi.responses import Response
from models.players import SummonerRequest, SummonerResponse, PlayerStatsResponse
from models.match import RecentGameSummary, FullGameData
from services.player_service import PlayerService
from dependency.dependencies import get_player_service
from middleware.auth import get_current_user
from typing import List
from utils.logger import logger
import asyncio


router = APIRouter(prefix="/api/players", tags=["players"])

@router.options("/summoner")
async def options_summoner(request):
    """Handle OPTIONS preflight requests"""
    origin = request.headers.get("origin", "*")
    return Response(
        status_code=200,
        headers={
            "Access-Control-Allow-Origin": origin,
            "Access-Control-Allow-Methods": "GET, POST, OPTIONS",
            "Access-Control-Allow-Headers": "Content-Type, Authorization",
            "Access-Control-Allow-Credentials": "true",
            "Access-Control-Max-Age": "3600",
        }
    )

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


@router.get("/recent-games", response_model=List[RecentGameSummary])
async def get_recent_games(
    count: int = 10,
    current_user: str = Depends(get_current_user),
    player_service: PlayerService = Depends(get_player_service)
):
    """Get player's recent games (separate endpoint for performance)"""
    logger.info(f"GET /api/players/recent-games - User: {current_user}")
    return await player_service.get_recent_games(current_user, count)


@router.get("/games", response_model=List[FullGameData])
async def get_games(
    start_index: int = Query(0, ge=0, description="Starting index for pagination (0-based)"),
    count: int = Query(10, ge=1, le=50, description="Number of games to fetch (1-50)"),
    current_user: str = Depends(get_current_user),
    player_service: PlayerService = Depends(get_player_service)
):
    """
    Get games with full match and timeline data from DB only (no API calls).
    Uses pagination with start_index and count.
    
    - **start_index**: Starting index (0-based) for pagination
    - **count**: Number of games to fetch (default 10, max 50)
    
    Returns full match data and timeline data for each game.
    """
    logger.info(f"GET /api/players/games - User: {current_user}, start_index: {start_index}, count: {count}")
    return await player_service.get_games(current_user, start_index, count)


@router.post("/sync-matches")
async def sync_match_history(
    current_user: str = Depends(get_current_user),
    player_service: PlayerService = Depends(get_player_service)
):
    """
    Manually sync match history for the current user (non-blocking).
    Triggers background sync and returns immediately.
    """
    # Get user's summoner
    summoner = await player_service.get_summoner(current_user)
    
    # Trigger background sync (non-blocking)
    asyncio.create_task(
        player_service.sync_match_history(summoner.puuid, summoner.region)
    )
    
    return {
        "success": True,
        "message": "Match history sync started in background. Check /sync-status for progress."
    }


@router.get("/sync-status")
async def check_sync_status(
    current_user: str = Depends(get_current_user),
    player_service: PlayerService = Depends(get_player_service)
):
    """Check if match history is up to date"""
    # Get user's summoner
    summoner = await player_service.get_summoner(current_user)
    
    # Check sync status
    is_synced = await player_service.is_match_history_synced(summoner.puuid, summoner.region)
    
    return {
        "is_synced": is_synced,
        "message": "Match history is up to date" if is_synced else "New matches available to sync"
    }


@router.get("/match/{match_id}", response_model=FullGameData)
async def get_match(
    match_id: str,
    current_user: str = Depends(get_current_user),
    player_service: PlayerService = Depends(get_player_service)
):
    """
    Get a specific match by match_id with full match data and timeline.
    Returns match data and timeline for the specified match.
    User must have participated in the match.
    """
    logger.info(f"GET /api/players/match/{match_id} - User: {current_user}")
    return await player_service.get_match_by_id(current_user, match_id)
