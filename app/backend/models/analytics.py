"""
Analytics and performance evaluation models
"""
from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any


class PerformanceMetrics(BaseModel):
    """Performance metrics for a single game"""
    match_id: str
    participant_id: int
    kda: float
    cs_per_min: float
    gold_per_min: float
    damage_per_min: float
    vision_score: int
    kill_participation: float
    
    class Config:
        extra = "allow"


class GamePhaseAnalysis(BaseModel):
    """Analysis of specific game phase"""
    phase: str = Field(..., pattern="^(early|mid|late)$")
    cs_advantage: float
    gold_advantage: float
    xp_advantage: float
    deaths: int
    kills: int
    assists: int


class PerformanceAnalysisRequest(BaseModel):
    """Request model for performance analysis"""
    match_id: str
    summoner_id: str
    include_timeline: bool = True


class PerformanceAnalysisResponse(BaseModel):
    """Response model for performance analysis"""
    match_id: str
    summoner_id: str
    overall_grade: str = Field(..., pattern="^(S|A|B|C|D|F)$")
    metrics: PerformanceMetrics
    phase_analysis: List[GamePhaseAnalysis]
    strengths: List[str]
    weaknesses: List[str]
    recommendations: List[str]
    
    class Config:
        extra = "allow"


class SkillProgressionRequest(BaseModel):
    """Request model for skill progression tracking"""
    summoner_id: str
    champion_id: Optional[str] = None
    time_range_days: int = Field(30, ge=1, le=365)


class SkillProgressionResponse(BaseModel):
    """Response model for skill progression"""
    summoner_id: str
    champion_id: Optional[str] = None
    time_range_days: int
    games_analyzed: int
    improvement_metrics: Dict[str, float]
    skill_trends: Dict[str, List[float]]
    current_rank: Optional[str] = None
    
    class Config:
        extra = "allow"


class InsightRequest(BaseModel):
    """Request model for AI-generated insights"""
    summoner_id: str
    match_ids: List[str] = Field(..., min_items=1, max_items=10)
    focus_areas: Optional[List[str]] = None


class InsightResponse(BaseModel):
    """Response model for AI-generated insights"""
    summoner_id: str
    insights: List[str]
    key_patterns: List[str]
    actionable_tips: List[str]
    champion_pool_suggestions: List[str]
    
    class Config:
        extra = "allow"
