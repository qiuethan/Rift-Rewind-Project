"""
Tracked Champions Models
Pydantic models for champion tracking feature
"""
from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime


class TrackChampionRequest(BaseModel):
    """Request to track a champion"""
    champion_id: int = Field(..., gt=0, description="Champion ID to track")
    
    class Config:
        extra = "forbid"


class UntrackChampionRequest(BaseModel):
    """Request to untrack a champion"""
    champion_id: int = Field(..., gt=0, description="Champion ID to untrack")
    
    class Config:
        extra = "forbid"


class TrackedChampion(BaseModel):
    """Tracked champion data"""
    champion_id: int
    tracked_at: datetime
    
    class Config:
        extra = "allow"


class TrackedChampionsResponse(BaseModel):
    """Response containing user's tracked champions"""
    tracked_champions: List[TrackedChampion] = Field(default_factory=list)
    count: int = Field(default=0, description="Number of tracked champions")
    max_allowed: int = Field(default=3, description="Maximum champions allowed")
    
    class Config:
        extra = "allow"


class TrackChampionResponse(BaseModel):
    """Response after tracking a champion"""
    message: str
    champion_id: int
    tracked_at: datetime
    
    class Config:
        extra = "allow"
