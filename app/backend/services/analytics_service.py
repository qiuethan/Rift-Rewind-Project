"""
Analytics service - Orchestrates analytics operations
"""
from repositories.analytics_repository import AnalyticsRepository
from repositories.match_repository import MatchRepository
from domain.analytics_domain import AnalyticsDomain
from models.analytics import (
    PerformanceAnalysisRequest,
    PerformanceAnalysisResponse,
    SkillProgressionRequest,
    SkillProgressionResponse,
    InsightRequest,
    InsightResponse,
    PerformanceMetrics,
    GamePhaseAnalysis
)
from fastapi import HTTPException, status
from typing import List


class AnalyticsService:
    """Service for analytics operations - pure orchestration"""
    
    def __init__(
        self,
        analytics_repository: AnalyticsRepository,
        match_repository: MatchRepository,
        analytics_domain: AnalyticsDomain
    ):
        self.analytics_repository = analytics_repository
        self.match_repository = match_repository
        self.analytics_domain = analytics_domain
    
    async def analyze_performance(
        self,
        request: PerformanceAnalysisRequest
    ) -> PerformanceAnalysisResponse:
        """Analyze player performance in a match"""
        # Check cache first
        cached = await self.analytics_repository.get_cached_analysis(
            request.match_id,
            request.summoner_id
        )
        if cached:
            return PerformanceAnalysisResponse(**cached)
        
        # Get performance metrics
        metrics = await self.analytics_repository.get_performance_metrics(
            request.match_id,
            request.summoner_id
        )
        
        if not metrics:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Performance metrics not found"
            )
        
        # Calculate grade
        metrics_dict = metrics.dict()
        grade = self.analytics_domain.calculate_performance_grade(metrics_dict)
        
        # Identify strengths and weaknesses
        strengths = self.analytics_domain.identify_strengths(metrics_dict)
        weaknesses = self.analytics_domain.identify_weaknesses(metrics_dict)
        
        # Generate recommendations
        recommendations = self.analytics_domain.generate_recommendations(strengths, weaknesses)
        
        # Create phase analysis (demo)
        phase_analysis = [
            GamePhaseAnalysis(
                phase="early",
                cs_advantage=5.0,
                gold_advantage=200.0,
                xp_advantage=100.0,
                deaths=0,
                kills=1,
                assists=2
            ),
            GamePhaseAnalysis(
                phase="mid",
                cs_advantage=-10.0,
                gold_advantage=-300.0,
                xp_advantage=-150.0,
                deaths=2,
                kills=2,
                assists=3
            ),
            GamePhaseAnalysis(
                phase="late",
                cs_advantage=0.0,
                gold_advantage=100.0,
                xp_advantage=50.0,
                deaths=1,
                kills=2,
                assists=5
            )
        ]
        
        analysis = PerformanceAnalysisResponse(
            match_id=request.match_id,
            summoner_id=request.summoner_id,
            overall_grade=grade,
            metrics=metrics,
            phase_analysis=phase_analysis,
            strengths=strengths,
            weaknesses=weaknesses,
            recommendations=recommendations
        )
        
        # Save to cache
        await self.analytics_repository.save_analysis(
            request.match_id,
            request.summoner_id,
            analysis.dict()
        )
        
        return analysis
    
    async def get_skill_progression(
        self,
        request: SkillProgressionRequest
    ) -> SkillProgressionResponse:
        """Get skill progression over time"""
        # Validate
        self.analytics_domain.validate_time_range(request.time_range_days)
        
        # Calculate progression
        progression = await self.analytics_repository.calculate_skill_progression(
            request.summoner_id,
            request.time_range_days
        )
        
        if not progression:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Skill progression data not found"
            )
        
        return progression
    
    async def generate_insights(self, request: InsightRequest) -> InsightResponse:
        """Generate AI-powered insights"""
        # Validate
        self.analytics_domain.validate_match_list(request.match_ids)
        
        # Generate insights using LLM
        insights_data = await self.analytics_repository.generate_insights(
            request.summoner_id,
            request.match_ids
        )
        
        return InsightResponse(
            summoner_id=request.summoner_id,
            insights=insights_data.get('insights', []),
            key_patterns=insights_data.get('key_patterns', []),
            actionable_tips=insights_data.get('actionable_tips', []),
            champion_pool_suggestions=insights_data.get('champion_pool_suggestions', [])
        )
