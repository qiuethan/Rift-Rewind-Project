"""
Player and summoner models
"""
from pydantic import BaseModel, Field
from typing import Optional, List


class SummonerRequest(BaseModel):
    """Request model for linking summoner account"""
    summoner_name: str = Field(..., min_length=3, max_length=16)
    region: str = Field(..., pattern="^(NA1|EUW1|EUN1|KR|BR1|JP1|LA1|LA2|OC1|TR1|RU)$")
    tag_line: Optional[str] = Field(None, max_length=5)


class SummonerResponse(BaseModel):
    """Response model for summoner data"""
    id: str
    summoner_name: str
    region: str
    puuid: str
    summoner_level: int
    profile_icon_id: int
    last_updated: str
    
    class Config:
        extra = "allow"


class PlayerStatsResponse(BaseModel):
    """Response model for player statistics"""
    summoner_id: str
    total_games: int
    wins: int
    losses: int
    win_rate: float
    favorite_champions: List[str]
    average_kda: float
    average_cs_per_min: float
    
    class Config:
        extra = "allow"
