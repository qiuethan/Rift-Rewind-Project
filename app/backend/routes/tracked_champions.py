"""
Tracked Champions Routes
HTTP endpoints for tracked champions feature
"""
from fastapi import APIRouter, Depends, status
from models.tracked_champions import (
    TrackedChampionsResponse,
    TrackChampionRequest,
    TrackChampionResponse,
    UntrackChampionRequest
)
from services.tracked_champions_service import TrackedChampionsService
from dependency.dependencies import get_tracked_champions_service
from middleware.auth import get_current_user


router = APIRouter(prefix="/api/tracked-champions", tags=["tracked-champions"])


@router.get("", response_model=TrackedChampionsResponse)
async def get_tracked_champions(
    current_user: str = Depends(get_current_user),
    service: TrackedChampionsService = Depends(get_tracked_champions_service)
):
    """Get user's tracked champions"""
    return await service.get_tracked_champions(current_user)


@router.post("", response_model=TrackChampionResponse, status_code=status.HTTP_201_CREATED)
async def track_champion(
    request: TrackChampionRequest,
    current_user: str = Depends(get_current_user),
    service: TrackedChampionsService = Depends(get_tracked_champions_service)
):
    """Add a champion to user's tracked list"""
    return await service.track_champion(current_user, request)


@router.delete("/{champion_id}")
async def untrack_champion(
    champion_id: int,
    current_user: str = Depends(get_current_user),
    service: TrackedChampionsService = Depends(get_tracked_champions_service)
):
    """Remove a champion from user's tracked list"""
    request = UntrackChampionRequest(champion_id=champion_id)
    return await service.untrack_champion(current_user, request)
