"""Models module exports"""
from models.auth import (
    RegisterRequest,
    LoginRequest,
    AuthResponse,
    TokenResponse
)
from models.players import (
    SummonerRequest,
    SummonerResponse,
    PlayerStatsResponse
)
from models.matches import (
    MatchRequest,
    MatchTimelineResponse,
    MatchSummaryResponse,
    ParticipantFrame,
    GameEvent
)
from models.champions import (
    ChampionData,
    ChampionRecommendationRequest,
    ChampionRecommendationResponse,
    ChampionSimilarityRequest,
    ChampionSimilarityResponse
)
from models.analytics import (
    PerformanceAnalysisRequest,
    PerformanceAnalysisResponse,
    SkillProgressionRequest,
    SkillProgressionResponse,
    InsightRequest,
    InsightResponse
)

__all__ = [
    # Auth
    'RegisterRequest',
    'LoginRequest',
    'AuthResponse',
    'TokenResponse',
    # Players
    'SummonerRequest',
    'SummonerResponse',
    'PlayerStatsResponse',
    # Matches
    'MatchRequest',
    'MatchTimelineResponse',
    'MatchSummaryResponse',
    'ParticipantFrame',
    'GameEvent',
    # Champions
    'ChampionData',
    'ChampionRecommendationRequest',
    'ChampionRecommendationResponse',
    'ChampionSimilarityRequest',
    'ChampionSimilarityResponse',
    # Analytics
    'PerformanceAnalysisRequest',
    'PerformanceAnalysisResponse',
    'SkillProgressionRequest',
    'SkillProgressionResponse',
    'InsightRequest',
    'InsightResponse',
]
