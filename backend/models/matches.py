"""
Match and game timeline models
"""
from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any


class MatchRequest(BaseModel):
    """Request model for fetching match data"""
    match_id: str
    region: str = "americas"


class ParticipantFrame(BaseModel):
    """Participant frame data from timeline"""
    participant_id: int
    level: int
    current_gold: int
    total_gold: int
    xp: int
    minions_killed: int
    jungle_minions_killed: int
    champion_stats: Dict[str, Any]
    damage_stats: Dict[str, Any]
    position: Dict[str, float]


class GameEvent(BaseModel):
    """Game event from timeline"""
    type: str
    timestamp: int
    participant_id: Optional[int] = None
    
    class Config:
        extra = "allow"


class MatchTimelineResponse(BaseModel):
    """Response model for match timeline"""
    match_id: str
    frames: List[Dict[str, Any]]
    frame_interval: int
    
    class Config:
        extra = "allow"


class MatchSummaryResponse(BaseModel):
    """Response model for match summary"""
    match_id: str
    game_duration: int
    game_mode: str
    game_type: str
    participants: List[Dict[str, Any]]
    teams: List[Dict[str, Any]]
    
    class Config:
        extra = "allow"
