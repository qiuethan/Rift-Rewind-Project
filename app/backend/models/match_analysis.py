"""
Models for match analysis data
"""
from pydantic import BaseModel
from typing import Dict, List, Optional, Any


class PlayerAnalysis(BaseModel):
    """Analysis data for a single player in the match"""
    participant_id: int
    champion_id: int
    champion_name: str
    
    # Early game stats (0-15 min)
    early_game_gold: int
    early_game_cs: int
    early_game_xp: int
    early_game_kills: int
    early_game_deaths: int
    early_game_assists: int
    
    # Mid game stats (15-25 min)
    mid_game_gold: int
    mid_game_cs: int
    mid_game_xp: int
    mid_game_kills: int
    mid_game_deaths: int
    mid_game_assists: int
    
    # Late game stats (25+ min)
    late_game_gold: int
    late_game_cs: int
    late_game_xp: int
    late_game_kills: int
    late_game_deaths: int
    late_game_assists: int
    
    # Performance metrics
    gold_per_minute: float
    cs_per_minute: float
    xp_per_minute: float
    damage_per_minute: float
    vision_score_per_minute: float
    
    # Combat stats
    total_damage_dealt: int
    damage_to_champions: int
    damage_taken: int
    healing_done: int
    vision_score: int
    
    # Objective participation
    turret_damage: int
    objective_damage: int
    epic_monster_kills: int
    
    class Config:
        extra = "allow"


class TeamAnalysis(BaseModel):
    """Analysis data for a team in the match"""
    team_id: int
    
    # Objective control
    dragons_killed: int
    barons_killed: int
    towers_destroyed: int
    inhibitors_destroyed: int
    
    # Team stats by game phase
    early_game_gold: int
    mid_game_gold: int
    late_game_gold: int
    
    # Team fight analysis
    team_fight_wins: int
    team_fight_losses: int
    
    # Vision control
    vision_score: int
    wards_placed: int
    wards_destroyed: int
    
    class Config:
        extra = "allow"


class MatchAnalysis(BaseModel):
    """Complete match analysis data"""
    match_id: str
    game_duration: int
    game_mode: str
    
    # Player analysis
    player_analysis: Dict[int, PlayerAnalysis]  # Keyed by participant_id
    
    # Team analysis
    team_analysis: Dict[int, TeamAnalysis]  # Keyed by team_id
    
    # Game phase timing
    early_game_end: int  # Timestamp when early game ends
    mid_game_end: int    # Timestamp when mid game ends
    
    # Game state analysis
    gold_difference_timeline: List[Dict[str, float]]  # Timeline of gold differences
    xp_difference_timeline: List[Dict[str, float]]    # Timeline of xp differences
    
    # Match summary stats
    total_kills: int
    game_pace_score: float  # Measure of how action-packed the game was
    comeback_factor: float  # Measure of how much the game swung
    
    class Config:
        extra = "allow"