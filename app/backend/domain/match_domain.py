"""
Match domain - Pure business logic for match operations
"""
from fastapi import HTTPException, status
from typing import Dict, Any, List


class MatchDomain:
    """Pure business logic for match operations"""
    
    def __init__(self):
        pass
    
    def validate_match_id(self, match_id: str) -> None:
        """Validate match ID format"""
        if not match_id or len(match_id) < 10:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid match ID format"
            )
    
    def validate_region(self, region: str) -> None:
        """Validate region for match data"""
        valid_regions = ["americas", "asia", "europe", "sea"]
        if region not in valid_regions:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Region must be one of: {', '.join(valid_regions)}"
            )
    
    def calculate_cs_per_min(self, minions_killed: int, jungle_minions: int, game_duration_seconds: int) -> float:
        """Calculate CS per minute"""
        if game_duration_seconds == 0:
            return 0.0
        
        total_cs = minions_killed + jungle_minions
        minutes = game_duration_seconds / 60
        return round(total_cs / minutes, 2)
    
    def calculate_gold_per_min(self, total_gold: int, game_duration_seconds: int) -> float:
        """Calculate gold per minute"""
        if game_duration_seconds == 0:
            return 0.0
        
        minutes = game_duration_seconds / 60
        return round(total_gold / minutes, 2)
    
    def determine_game_phase(self, timestamp_ms: int) -> str:
        """Determine game phase based on timestamp"""
        minutes = timestamp_ms / 60000
        
        if minutes <= 15:
            return "early"
        elif minutes <= 30:
            return "mid"
        else:
            return "late"
    
    def calculate_kill_participation(self, kills: int, assists: int, team_kills: int) -> float:
        """Calculate kill participation percentage"""
        if team_kills == 0:
            return 0.0
        
        participation = (kills + assists) / team_kills
        return round(participation * 100, 2)
    
    def validate_participant_id(self, participant_id: int) -> None:
        """Validate participant ID"""
        if participant_id < 1 or participant_id > 10:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Participant ID must be between 1 and 10"
            )
