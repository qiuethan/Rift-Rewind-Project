"""
Analytics repository interface - Abstract contract for analytics data access
"""
from abc import ABC, abstractmethod
from typing import Optional, List, Dict, Any
from models.analytics import PerformanceMetrics, SkillProgressionResponse


class AnalyticsRepository(ABC):
    """Abstract interface for analytics data access"""
    
    @abstractmethod
    async def save_performance_metrics(self, match_id: str, metrics: dict) -> Optional[PerformanceMetrics]:
        """Save performance metrics to database, or None if failed"""
        pass
    
    @abstractmethod
    async def get_performance_metrics(self, match_id: str, summoner_id: str) -> Optional[PerformanceMetrics]:
        """Get performance metrics from database"""
        pass
    
    @abstractmethod
    async def get_historical_metrics(self, summoner_id: str, days: int) -> List[PerformanceMetrics]:
        """Get historical performance metrics"""
        pass
    
    @abstractmethod
    async def calculate_skill_progression(self, summoner_id: str, days: int) -> Optional[SkillProgressionResponse]:
        """Calculate skill progression over time"""
        pass
    
    @abstractmethod
    async def save_analysis(self, match_id: str, summoner_id: str, analysis_data: dict) -> Optional[dict]:
        """Save performance analysis to database, or None if failed"""
        pass
    
    @abstractmethod
    async def get_cached_analysis(self, match_id: str, summoner_id: str) -> Optional[dict]:
        """Get cached performance analysis"""
        pass
    
    @abstractmethod
    async def generate_insights(self, summoner_id: str, match_ids: List[str]) -> Dict[str, Any]:
        """Generate AI insights using LLM"""
        pass
