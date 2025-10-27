"""
Riot API Response Models
"""
from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any


# ============================================================================
# ACCOUNT API MODELS
# ============================================================================

class AccountResponse(BaseModel):
    """Response from Riot Account API"""
    puuid: str
    game_name: str = Field(alias="gameName")
    tag_line: str = Field(alias="tagLine")
    
    class Config:
        populate_by_name = True
        extra = "allow"


# ============================================================================
# SUMMONER API MODELS
# ============================================================================

class SummonerAPIResponse(BaseModel):
    """Response from Riot Summoner API"""
    id: str  # Encrypted summoner ID
    account_id: str = Field(alias="accountId")
    puuid: str
    name: str
    profile_icon_id: int = Field(alias="profileIconId")
    revision_date: int = Field(alias="revisionDate")
    summoner_level: int = Field(alias="summonerLevel")
    
    class Config:
        populate_by_name = True
        extra = "allow"


# ============================================================================
# LEAGUE API MODELS (Ranked)
# ============================================================================

class MiniSeriesDTO(BaseModel):
    """Mini series data for promotion series"""
    losses: int
    progress: str
    target: int
    wins: int
    
    class Config:
        extra = "allow"


class LeagueEntryResponse(BaseModel):
    """Response from League API - single ranked queue entry"""
    league_id: str = Field(alias="leagueId")
    summoner_id: str = Field(alias="summonerId")
    summoner_name: str = Field(alias="summonerName")
    queue_type: str = Field(alias="queueType")  # RANKED_SOLO_5x5, RANKED_FLEX_SR
    tier: str  # IRON, BRONZE, SILVER, GOLD, PLATINUM, EMERALD, DIAMOND, MASTER, GRANDMASTER, CHALLENGER
    rank: str  # I, II, III, IV (not applicable for MASTER+)
    league_points: int = Field(alias="leaguePoints")
    wins: int
    losses: int
    hot_streak: bool = Field(alias="hotStreak")
    veteran: bool
    fresh_blood: bool = Field(alias="freshBlood")
    inactive: bool
    mini_series: Optional[MiniSeriesDTO] = Field(None, alias="miniSeries")
    
    class Config:
        populate_by_name = True
        extra = "allow"


# ============================================================================
# CHAMPION MASTERY API MODELS
# ============================================================================

class NextSeasonMilestone(BaseModel):
    """Next season milestone requirements"""
    require_grade_counts: Dict[str, int] = Field(alias="requireGradeCounts")
    reward_marks: int = Field(alias="rewardMarks")
    bonus: bool
    total_games_requires: int = Field(alias="totalGamesRequires")
    
    class Config:
        populate_by_name = True
        extra = "allow"


class ChampionMasteryResponse(BaseModel):
    """
    Response from Champion Mastery API
    
    IMPORTANT FOR FRONTEND:
    - When fetched from Riot API: Uses camelCase (championId, championLevel, etc.)
    - When stored in DB: Converted to snake_case (champion_id, champion_level, etc.)
    - When retrieved from DB: Returns snake_case fields
    
    Frontend should handle both formats:
    - Use championId || champion_id
    - Use championLevel || champion_level
    - Use championPoints || champion_points
    - etc.
    """
    puuid: str
    champion_id: int = Field(alias="championId")
    champion_level: int = Field(alias="championLevel")
    champion_points: int = Field(alias="championPoints")
    last_play_time: int = Field(alias="lastPlayTime")  # Unix timestamp in milliseconds
    champion_points_since_last_level: int = Field(alias="championPointsSinceLastLevel")
    champion_points_until_next_level: int = Field(alias="championPointsUntilNextLevel")
    mark_required_for_next_level: int = Field(alias="markRequiredForNextLevel")
    tokens_earned: int = Field(alias="tokensEarned")
    champion_season_milestone: int = Field(alias="championSeasonMilestone")
    next_season_milestone: Optional[NextSeasonMilestone] = Field(None, alias="nextSeasonMilestone")
    chest_granted: Optional[bool] = Field(None, alias="chestGranted")  # Legacy field
    
    class Config:
        populate_by_name = True
        extra = "allow"


class MasteryScoreResponse(BaseModel):
    """Response from Mastery Score API - just an integer"""
    score: int
    
    class Config:
        extra = "allow"


# ============================================================================
# AGGREGATED MODELS (for internal use)
# ============================================================================

class RankedData(BaseModel):
    """Aggregated ranked data from all queues"""
    ranked_solo_tier: Optional[str] = None
    ranked_solo_rank: Optional[str] = None
    ranked_solo_lp: Optional[int] = None
    ranked_solo_wins: Optional[int] = None
    ranked_solo_losses: Optional[int] = None
    ranked_flex_tier: Optional[str] = None
    ranked_flex_rank: Optional[str] = None
    ranked_flex_lp: Optional[int] = None
    ranked_flex_wins: Optional[int] = None
    ranked_flex_losses: Optional[int] = None
    
    @classmethod
    def from_league_entries(cls, league_entries: List[LeagueEntryResponse]) -> 'RankedData':
        """Create RankedData from list of league entries"""
        data = {}
        
        for entry in league_entries:
            if entry.queue_type == 'RANKED_SOLO_5x5':
                data['ranked_solo_tier'] = entry.tier
                data['ranked_solo_rank'] = entry.rank
                data['ranked_solo_lp'] = entry.league_points
                data['ranked_solo_wins'] = entry.wins
                data['ranked_solo_losses'] = entry.losses
            elif entry.queue_type == 'RANKED_FLEX_SR':
                data['ranked_flex_tier'] = entry.tier
                data['ranked_flex_rank'] = entry.rank
                data['ranked_flex_lp'] = entry.league_points
                data['ranked_flex_wins'] = entry.wins
                data['ranked_flex_losses'] = entry.losses
        
        return cls(**data)
    
    @classmethod
    def from_dict_entries(cls, league_entries: List[dict]) -> 'RankedData':
        """Create RankedData from list of dict entries (raw API response)"""
        data = {}
        
        for entry in league_entries:
            queue_type = entry.get('queueType')
            
            if queue_type == 'RANKED_SOLO_5x5':
                data['ranked_solo_tier'] = entry.get('tier')
                data['ranked_solo_rank'] = entry.get('rank')
                data['ranked_solo_lp'] = entry.get('leaguePoints')
                data['ranked_solo_wins'] = entry.get('wins')
                data['ranked_solo_losses'] = entry.get('losses')
            elif queue_type == 'RANKED_FLEX_SR':
                data['ranked_flex_tier'] = entry.get('tier')
                data['ranked_flex_rank'] = entry.get('rank')
                data['ranked_flex_lp'] = entry.get('leaguePoints')
                data['ranked_flex_wins'] = entry.get('wins')
                data['ranked_flex_losses'] = entry.get('losses')
        
        return cls(**data)
    
    def to_dict(self) -> dict:
        """Convert to dictionary for database storage"""
        return self.dict(exclude_none=False)
    
    class Config:
        extra = "allow"


class MasteryData(BaseModel):
    """Aggregated champion mastery data"""
    champion_masteries: List[ChampionMasteryResponse] = []
    top_champions: List[ChampionMasteryResponse] = []
    total_mastery_score: Optional[int] = None
    
    @classmethod
    def from_api_data(cls, all_masteries: List[dict], mastery_score: Optional[int] = None) -> 'MasteryData':
        """Create MasteryData from API responses"""
        validated_masteries = [ChampionMasteryResponse(**m) for m in all_masteries] if all_masteries else []
        return cls(
            champion_masteries=validated_masteries,
            top_champions=validated_masteries[:10],
            total_mastery_score=mastery_score
        )
    
    def to_dict(self) -> dict:
        """
        Convert to dictionary for database storage
        Excludes top_champions as it's computed from champion_masteries
        """
        data = self.dict(exclude_none=False)
        # Convert models to dicts for JSONB storage
        if data.get('champion_masteries'):
            data['champion_masteries'] = [m.dict() if hasattr(m, 'dict') else m for m in data['champion_masteries']]
        data.pop('top_champions', None)
        return data
    
    class Config:
        extra = "allow"


class MatchHistoryResponse(BaseModel):
    """Response model for match history"""
    puuid: str
    match_ids: List[str]
    count: int
    
    class Config:
        extra = "allow"
