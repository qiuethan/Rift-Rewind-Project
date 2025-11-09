"""
Champion Progress Models - Data validation & serialization
Following Clean Architecture: Pure data structures with Pydantic validation
"""
from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime


class ChampionMatchScore(BaseModel):
    """Individual match score for a champion"""
    match_id: str
    champion_id: int
    champion_name: str
    game_date: int = Field(..., description="Unix timestamp of game")
    eps_score: float = Field(..., description="End-Game Performance Score - player skill performance")
    cps_score: float = Field(..., description="Cumulative Power Score - champion power/strength in-game")
    kda: float = Field(..., description="KDA ratio")
    win: bool
    kills: int
    deaths: int
    assists: int
    cs: int
    gold: int
    damage: int
    vision_score: int


class ChampionProgressTrend(BaseModel):
    """Trend data for a champion over time"""
    champion_id: int
    champion_name: str
    total_games: int
    wins: int
    losses: int
    win_rate: float
    avg_eps_score: float
    avg_cps_score: float
    avg_kda: float
    recent_trend: float = Field(0.0, description="Combined trend percentage (deprecated, use eps_trend/cps_trend)")
    eps_trend: float = Field(0.0, description="EPS trend percentage per game (positive = improving, negative = declining)")
    cps_trend: float = Field(0.0, description="CPS trend percentage per game (positive = improving, negative = declining)")
    last_played: int = Field(..., description="Unix timestamp of last game")
    mastery_level: Optional[int] = None
    mastery_points: Optional[int] = None


class ChampionProgressRequest(BaseModel):
    """Request to get champion progress"""
    champion_id: Optional[int] = Field(None, description="Specific champion ID, or None for all")
    limit: int = Field(10, ge=1, le=100, description="Number of matches to include")
    
    class Config:
        extra = "forbid"


class ChampionProgressResponse(BaseModel):
    """Response with champion progress data"""
    user_id: str
    champion_id: int
    champion_name: str
    trend: ChampionProgressTrend
    recent_matches: List[ChampionMatchScore]
    performance_summary: Dict[str, Any] = Field(
        default_factory=dict,
        description="Additional performance metrics"
    )
    
    class Config:
        extra = "allow"


class AllChampionsProgressResponse(BaseModel):
    """Response with progress for all champions"""
    user_id: str
    champions: List[ChampionProgressTrend]
    total_champions_played: int
    most_played_champion: Optional[ChampionProgressTrend] = None
    best_performing_champion: Optional[ChampionProgressTrend] = None
    
    class Config:
        extra = "allow"


class ChampionProgressRecord(BaseModel):
    """Database record for champion_progress table"""
    id: Optional[str] = None
    user_id: str
    puuid: str
    champion_id: int
    champion_name: str
    total_games: int = 0
    wins: int = 0
    losses: int = 0
    win_rate: float = 0.0
    avg_eps_score: float = 0.0
    avg_cps_score: float = 0.0
    avg_kda: float = 0.0
    recent_trend: float = 0.0  # Combined trend percentage (deprecated)
    eps_trend: float = 0.0  # EPS trend percentage per game
    cps_trend: float = 0.0  # CPS trend percentage per game
    last_played: int = Field(..., description="Unix timestamp")
    recent_matches: List[Dict[str, Any]] = Field(default_factory=list)
    performance_history: List[Dict[str, Any]] = Field(default_factory=list)
    created_at: Optional[str] = None
    updated_at: Optional[str] = None
    
    @classmethod
    def from_dict(cls, data: dict) -> 'ChampionProgressRecord':
        """Create from dictionary"""
        return cls(**data)
    
    def to_db_dict(self) -> dict:
        """Convert to database dictionary"""
        data = self.dict(exclude_none=False)
        # Remove id if None (let DB generate)
        if data.get('id') is None:
            data.pop('id', None)
        # Remove timestamps if None (let DB generate)
        if data.get('created_at') is None:
            data.pop('created_at', None)
        if data.get('updated_at') is None:
            data.pop('updated_at', None)
        return data
    
    def calculate_trend(self, previous_avg_eps: Optional[float] = None) -> str:
        """
        Calculate trend based on recent performance
        Returns: 'improving', 'declining', or 'stable'
        """
        if previous_avg_eps is None or len(self.performance_history) < 3:
            return "stable"
        
        # Compare current average to previous
        diff_percentage = ((self.avg_eps_score - previous_avg_eps) / previous_avg_eps) * 100
        
        if diff_percentage > 5:
            return "improving"
        elif diff_percentage < -5:
            return "declining"
        else:
            return "stable"


class UpdateChampionProgressRequest(BaseModel):
    """Request to update champion progress after a match"""
    match_id: str
    champion_id: int
    champion_name: str
    eps_score: float
    cps_score: float
    kda: float
    win: bool
    kills: int
    deaths: int
    assists: int
    cs: int
    gold: int
    damage: int
    vision_score: int
    game_date: int
    
    class Config:
        extra = "forbid"
