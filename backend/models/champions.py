"""
Champion models for recommendations and data
"""
from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any


class ChampionAbility(BaseModel):
    """Champion ability data"""
    name: str
    type: str
    description: str
    cooldown: Optional[List[float]] = None
    cost: Optional[List[int]] = None


class ChampionData(BaseModel):
    """Champion metadata"""
    id: str
    name: str
    title: str
    tags: List[str]
    stats: Dict[str, float]
    abilities: List[ChampionAbility]
    
    class Config:
        extra = "allow"


class ChampionRecommendationRequest(BaseModel):
    """Request model for champion recommendations"""
    summoner_id: str
    limit: int = Field(5, ge=1, le=20)
    include_reasoning: bool = True


class ChampionRecommendation(BaseModel):
    """Single champion recommendation"""
    champion_id: str
    champion_name: str
    similarity_score: float = Field(..., ge=0.0, le=1.0)
    reasoning: Optional[str] = None
    similar_abilities: Optional[List[str]] = None
    playstyle_match: Optional[str] = None


class ChampionRecommendationResponse(BaseModel):
    """Response model for champion recommendations"""
    summoner_id: str
    recommendations: List[ChampionRecommendation]
    based_on_champions: List[str]
    
    class Config:
        extra = "allow"


class ChampionSimilarityRequest(BaseModel):
    """Request model for champion similarity calculation"""
    champion_a: str
    champion_b: str
    include_details: bool = False


class ChampionSimilarityResponse(BaseModel):
    """Response model for champion similarity"""
    champion_a: str
    champion_b: str
    similarity_score: float
    ability_similarity: Optional[float] = None
    stat_similarity: Optional[float] = None
    playstyle_similarity: Optional[float] = None
    
    class Config:
        extra = "allow"
