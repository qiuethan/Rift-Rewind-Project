"""
Champion routes
"""
from fastapi import APIRouter, status, Depends
from models.champions import (
    ChampionData,
    ChampionRecommendationRequest,
    ChampionRecommendationResponse,
    ChampionSimilarityRequest,
    ChampionSimilarityResponse,
    AbilitySimilarityResponse
)
from services.champion_service import ChampionService
from dependency.dependencies import get_champion_service
from middleware.auth import get_current_user
from typing import List


router = APIRouter(prefix="/api/champions", tags=["champions"])


@router.get("/", response_model=List[ChampionData])
async def get_all_champions(
    champion_service: ChampionService = Depends(get_champion_service)
):
    """Get all champions (public endpoint)"""
    return await champion_service.get_all_champions()


@router.get("/{champion_id}", response_model=ChampionData)
async def get_champion(
    champion_id: str,
    champion_service: ChampionService = Depends(get_champion_service)
):
    """Get champion data by ID (public endpoint)"""
    return await champion_service.get_champion(champion_id)


@router.post("/recommendations", response_model=ChampionRecommendationResponse)
async def get_champion_recommendations(
    recommendation_request: ChampionRecommendationRequest,
    current_user: str = Depends(get_current_user),
    champion_service: ChampionService = Depends(get_champion_service)
):
    """Get champion recommendations for player (protected)"""
    return await champion_service.get_champion_recommendations(current_user, recommendation_request)


@router.get("/{champion_id}/ability-similarities", response_model=AbilitySimilarityResponse)
async def get_ability_similarities(
    champion_id: str,
    limit_per_ability: int = 3,
    current_user: str = Depends(get_current_user),
    champion_service: ChampionService = Depends(get_champion_service)
):
    """Get ability similarities for a champion's Q, W, E, R abilities filtered by user's champion pool (protected)"""
    return await champion_service.get_ability_similarities(current_user, champion_id, limit_per_ability)
