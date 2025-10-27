"""
Player and summoner models
"""
from pydantic import BaseModel, Field
from typing import Optional, List
from models.riot_api import ChampionMasteryResponse
from datetime import datetime


class SummonerRecord(BaseModel):
    """Database record for summoner table"""
    puuid: str
    summoner_id: Optional[str] = None  # Encrypted summoner ID for ranked API
    summoner_name: str
    game_name: Optional[str] = None
    tag_line: Optional[str] = None
    region: str
    summoner_level: int = 0
    profile_icon_id: int = 0
    
    ranked_solo_tier: Optional[str] = None
    ranked_solo_rank: Optional[str] = None
    ranked_solo_lp: Optional[int] = None
    ranked_solo_wins: Optional[int] = None
    ranked_solo_losses: Optional[int] = None
    ranked_flex_tier: Optional[str] = None
    ranked_flex_rank: Optional[str] = None
    
    champion_masteries: Optional[List[dict]] = None
    total_mastery_score: Optional[int] = None
    
    last_updated: Optional[str] = None
    
    @classmethod
    def from_summoner_data(cls, summoner_data: dict) -> 'SummonerRecord':
        """Create SummonerRecord from summoner data dictionary"""
        return cls(
            puuid=summoner_data.get('puuid'),
            summoner_id=summoner_data.get('id') or summoner_data.get('summoner_id'),
            summoner_name=summoner_data.get('summoner_name'),
            game_name=summoner_data.get('game_name'),
            tag_line=summoner_data.get('tag_line'),
            region=summoner_data.get('region'),
            summoner_level=summoner_data.get('summoner_level', 0),
            profile_icon_id=summoner_data.get('profile_icon_id', 0),
            ranked_solo_tier=summoner_data.get('ranked_solo_tier'),
            ranked_solo_rank=summoner_data.get('ranked_solo_rank'),
            ranked_solo_lp=summoner_data.get('ranked_solo_lp'),
            ranked_solo_wins=summoner_data.get('ranked_solo_wins'),
            ranked_solo_losses=summoner_data.get('ranked_solo_losses'),
            ranked_flex_tier=summoner_data.get('ranked_flex_tier'),
            ranked_flex_rank=summoner_data.get('ranked_flex_rank'),
            champion_masteries=summoner_data.get('champion_masteries'),
            total_mastery_score=summoner_data.get('total_mastery_score'),
            last_updated=summoner_data.get('last_updated')
        )
    
    def to_db_dict(self) -> dict:
        """Convert to dictionary for database insertion/update"""
        return self.dict(exclude_none=False)
    
    class Config:
        extra = "forbid"


class SummonerRequest(BaseModel):
    """Request model for linking summoner account"""
    summoner_name: Optional[str] = None
    game_name: Optional[str] = None
    tag_line: Optional[str] = None
    region: str = Field(..., pattern="^(americas|europe|asia|sea|NA1|EUW1|EUN1|KR|BR1|JP1|LA1|LA2|OC1|TR1|RU)$")
    
    class Config:
        extra = "forbid"


class SummonerResponse(BaseModel):
    """
    Response model for summoner data
    
    IMPORTANT FOR FRONTEND:
    Champion mastery data (champion_masteries, top_champions) contains objects with:
    - From Riot API (fresh data): camelCase fields (championId, championLevel, championPoints)
    - From Database (cached): snake_case fields (champion_id, champion_level, champion_points)
    
    Frontend should handle both formats by checking both field names:
        const championId = mastery.championId || mastery.champion_id;
        const championLevel = mastery.championLevel || mastery.champion_level;
        const championPoints = mastery.championPoints || mastery.champion_points;
    """
    id: str  
    summoner_name: str  
    game_name: Optional[str] = None
    tag_line: Optional[str] = None
    region: str
    puuid: str
    summoner_level: int
    profile_icon_id: int
    last_updated: str
    
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
    
    champion_masteries: Optional[List[dict]] = None
    top_champions: Optional[List[dict]] = None
    total_mastery_score: Optional[int] = None
    
    class Config:
        extra = "allow"


class PlayerStatsResponse(BaseModel):
    """Response model for player statistics and analytics"""
    summoner_id: str
    total_games: int
    wins: int
    losses: int
    win_rate: float
    favorite_champions: List[str]
    average_kda: float
    average_cs_per_min: float
    
    top_champions: Optional[List[ChampionMasteryResponse]] = None
    total_mastery_score: Optional[int] = None
    
    class Config:
        extra = "allow"


class PlayerProfile(BaseModel):
    """Complete player profile with all data"""
    summoner: SummonerResponse
    stats: Optional[PlayerStatsResponse] = None
    recent_matches: Optional[List[str]] = None
    
    class Config:
        extra = "allow"
