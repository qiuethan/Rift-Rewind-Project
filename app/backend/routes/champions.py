"""
Champion routes
"""
from fastapi import APIRouter, status, Depends
from models.champions import (
    ChampionData,
    ChampionRecommendationRequest,
    ChampionRecommendationResponse,
    ChampionSimilarityRequest,
    ChampionSimilarityResponse
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
    return await champion_service.get_champion_recommendations(recommendation_request)


@router.post("/similarity", response_model=ChampionSimilarityResponse)
async def calculate_champion_similarity(
    similarity_request: ChampionSimilarityRequest,
    champion_service: ChampionService = Depends(get_champion_service)
):
    """Calculate similarity between two champions (public endpoint)"""
    return await champion_service.calculate_similarity(similarity_request)
