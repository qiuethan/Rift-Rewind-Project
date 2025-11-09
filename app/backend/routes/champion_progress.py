"""
Champion Progress Routes - HTTP request/response handling
Following Clean Architecture: No business logic, delegates to service
"""
from fastapi import APIRouter, status, Depends, Query
from models.champion_progress import (
    ChampionProgressRequest,
    ChampionProgressResponse,
    AllChampionsProgressResponse,
    UpdateChampionProgressRequest
)
from services.champion_progress_service import ChampionProgressService
from dependency.dependencies import get_champion_progress_service
from middleware.auth import get_current_user
from utils.logger import logger


router = APIRouter(prefix="/api/champion-progress", tags=["champion-progress"])


@router.get("/champion/{champion_id}", response_model=ChampionProgressResponse)
async def get_champion_progress(
    champion_id: int,
    limit: int = Query(10, ge=1, le=100, description="Number of recent matches to include"),
    current_user: str = Depends(get_current_user),
    service: ChampionProgressService = Depends(get_champion_progress_service)
):
    """
    Get progress data for a specific champion
    
    - **champion_id**: Champion ID
    - **limit**: Number of recent matches to include (default 10, max 100)
    """
    logger.info(f"GET /api/champion-progress/champion/{champion_id} - User: {current_user}")
    
    request = ChampionProgressRequest(champion_id=champion_id, limit=limit)
    return await service.get_champion_progress(current_user, request)


@router.get("/all", response_model=AllChampionsProgressResponse)
async def get_all_champions_progress(
    current_user: str = Depends(get_current_user),
    service: ChampionProgressService = Depends(get_champion_progress_service)
):
    """
    Get progress data for all champions played by the user
    """
    logger.info(f"GET /api/champion-progress/all - User: {current_user}")
    return await service.get_all_champions_progress(current_user)


@router.post("/update", response_model=ChampionProgressResponse, status_code=status.HTTP_200_OK)
async def update_champion_progress(
    update_request: UpdateChampionProgressRequest,
    current_user: str = Depends(get_current_user),
    service: ChampionProgressService = Depends(get_champion_progress_service)
):
    """
    Update champion progress after a match (typically called internally after match analysis)
    
    This endpoint is used to update a player's champion-specific statistics and trends
    after completing a match.
    """
    logger.info(f"POST /api/champion-progress/update - User: {current_user}, Champion: {update_request.champion_id}")
    return await service.update_champion_progress_from_match(current_user, update_request)


@router.delete("/champion/{champion_id}", status_code=status.HTTP_200_OK)
async def delete_champion_progress(
    champion_id: int,
    current_user: str = Depends(get_current_user),
    service: ChampionProgressService = Depends(get_champion_progress_service)
):
    """
    Delete progress data for a specific champion
    
    - **champion_id**: Champion ID to delete progress for
    """
    logger.info(f"DELETE /api/champion-progress/champion/{champion_id} - User: {current_user}")
    return await service.delete_champion_progress(current_user, champion_id)


@router.delete("/all", status_code=status.HTTP_200_OK)
async def delete_all_champion_progress(
    current_user: str = Depends(get_current_user),
    service: ChampionProgressService = Depends(get_champion_progress_service)
):
    """
    Delete all champion progress data for the user
    """
    logger.info(f"DELETE /api/champion-progress/all - User: {current_user}")
    return await service.delete_champion_progress(current_user, None)
