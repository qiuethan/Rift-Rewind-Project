"""
Match data models for Match v5 API
"""
from pydantic import BaseModel
from typing import Optional, List, Dict, Any


class MatchParticipant(BaseModel):
    """Simplified participant data from a match"""
    puuid: str
    summoner_name: str
    champion_id: int
    champion_name: str
    kills: int
    deaths: int
    assists: int
    total_damage_dealt_to_champions: int
    gold_earned: int
    total_minions_killed: int
    vision_score: int
    items: List[int]
    win: bool
    
    class Config:
        extra = "allow"


class MatchInfo(BaseModel):
    """Match information"""
    game_id: str
    game_mode: str
    game_type: str
    game_duration: int  # in seconds
    game_creation: int  # timestamp in milliseconds
    game_end_timestamp: Optional[int] = None
    queue_id: int
    
    class Config:
        extra = "allow"


class RecentGameSummary(BaseModel):
    """Simplified recent game data for storage and display"""
    match_id: str
    game_mode: str
    game_duration: int  # in seconds
    game_creation: int  # timestamp in milliseconds
    champion_id: int
    champion_name: str
    kills: int
    deaths: int
    assists: int
    win: bool
    cs: int  # total minions killed
    gold: int
    damage: int
    vision_score: int
    items: List[int]
    
    class Config:
        extra = "allow"


class FullGameData(BaseModel):
    """Full game data including match data, timeline, and analysis"""
    match_id: str
    match_data: Dict[str, Any]  # Full match data from Riot API
    timeline_data: Optional[Dict[str, Any]] = None  # Timeline data from Riot API
    analysis: Optional[Dict[str, Any]] = None  # Computed analysis with Chart.js visualizations
    
    class Config:
        extra = "allow"
