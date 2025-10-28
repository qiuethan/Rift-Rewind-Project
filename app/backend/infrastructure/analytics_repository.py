"""
Analytics repository implementation with Supabase and LLM
"""
from repositories.analytics_repository import AnalyticsRepository
from models.analytics import PerformanceMetrics, SkillProgressionResponse
from infrastructure.database.database_client import DatabaseClient
from typing import Optional, List, Dict, Any


class AnalyticsRepositorySupabase(AnalyticsRepository):
    """Supabase + LLM implementation of analytics repository"""
    
    def __init__(self, client: DatabaseClient, openrouter_api_key: Optional[str] = None):
        self.client = client
        self.openrouter_api_key = openrouter_api_key
    
    async def save_performance_metrics(self, match_id: str, metrics: dict) -> Optional[PerformanceMetrics]:
        """Save performance metrics to database"""
        if self.client:
            metrics['match_id'] = match_id
            await self.client.table('performance_metrics').upsert(metrics).execute()
            return PerformanceMetrics(**metrics)
        return None
    
    async def get_performance_metrics(self, match_id: str, summoner_id: str) -> Optional[PerformanceMetrics]:
        """Get performance metrics from Firebase (DEMO)"""
        # Demo implementation
        return PerformanceMetrics(
            match_id=match_id,
            participant_id=1,
            kda=3.5,
            cs_per_min=7.2,
            gold_per_min=400,
            damage_per_min=600,
            vision_score=35,
            kill_participation=65.0
        )
    
    async def get_historical_metrics(self, summoner_id: str, days: int) -> List[PerformanceMetrics]:
        """Get historical performance metrics (DEMO)"""
        # Demo implementation
        return [
            PerformanceMetrics(
                match_id=f"match_{i}",
                participant_id=1,
                kda=3.0 + (i * 0.1),
                cs_per_min=7.0,
                gold_per_min=400,
                damage_per_min=600,
                vision_score=30,
                kill_participation=60.0
            )
            for i in range(10)
        ]
    
    async def calculate_skill_progression(self, summoner_id: str, days: int) -> Optional[SkillProgressionResponse]:
        """Calculate skill progression over time (DEMO)"""
        # Demo implementation
        return SkillProgressionResponse(
            summoner_id=summoner_id,
            time_range_days=days,
            games_analyzed=50,
            improvement_metrics={
                "kda": 0.5,
                "cs_per_min": 0.3,
                "vision_score": 5.0
            },
            skill_trends={
                "kda": [2.5, 2.7, 2.9, 3.1, 3.3],
                "cs_per_min": [6.5, 6.7, 6.9, 7.1, 7.3]
            },
            current_rank="Gold II"
        )
    
    async def save_analysis(self, match_id: str, summoner_id: str, analysis_data: dict) -> Optional[dict]:
        """Save performance analysis to database"""
        if self.client:
            analysis_data['match_id'] = match_id
            analysis_data['summoner_id'] = summoner_id
            await self.client.table('performance_analysis').upsert(analysis_data).execute()
            return analysis_data
        return None
    
    async def get_cached_analysis(self, match_id: str, summoner_id: str) -> Optional[dict]:
        """Get cached performance analysis from database"""
        if self.client:
            response = await self.client.table('performance_analysis').select('*').eq('match_id', match_id).eq('summoner_id', summoner_id).limit(1).execute()
            if response.data:
                return response.data[0]
        return None
    
    async def generate_insights(self, summoner_id: str, match_ids: List[str]) -> Dict[str, Any]:
        """Generate AI insights using LLM (DEMO)"""
        # Demo implementation - would call LLM API
        return {
            "insights": [
                "Your CS/min has improved by 15% over the last 10 games",
                "You tend to die more in mid-game teamfights - work on positioning",
                "Your vision score is above average for your rank"
            ],
            "key_patterns": [
                "Strong early game performance",
                "Consistent farming patterns"
            ],
            "actionable_tips": [
                "Focus on warding river before objectives spawn",
                "Practice team fight positioning in practice tool"
            ]
        }
