"""
Analytics routes
"""
from fastapi import APIRouter, status, Depends
from models.analytics import (
    PerformanceAnalysisRequest,
    PerformanceAnalysisResponse,
    SkillProgressionRequest,
    SkillProgressionResponse,
    InsightRequest,
    InsightResponse
)
from services.analytics_service import AnalyticsService
from dependency.dependencies import get_analytics_service
from middleware.auth import get_current_user


router = APIRouter(prefix="/api/analytics", tags=["analytics"])


@router.post("/performance", response_model=PerformanceAnalysisResponse)
async def analyze_performance(
    analysis_request: PerformanceAnalysisRequest,
    current_user: str = Depends(get_current_user),
    analytics_service: AnalyticsService = Depends(get_analytics_service)
):
    """Analyze player performance in a match (protected)"""
    return await analytics_service.analyze_performance(analysis_request)


@router.post("/progression", response_model=SkillProgressionResponse)
async def get_skill_progression(
    progression_request: SkillProgressionRequest,
    current_user: str = Depends(get_current_user),
    analytics_service: AnalyticsService = Depends(get_analytics_service)
):
    """Get skill progression over time (protected)"""
    return await analytics_service.get_skill_progression(progression_request)


@router.post("/insights", response_model=InsightResponse)
async def generate_insights(
    insight_request: InsightRequest,
    current_user: str = Depends(get_current_user),
    analytics_service: AnalyticsService = Depends(get_analytics_service)
):
    """Generate AI-powered insights (protected)"""
    return await analytics_service.generate_insights(insight_request)
