"""
Database Constants - Table names and other database-related constants
"""
from enum import Enum


class DatabaseTable(str, Enum):
    """Enum for database table names"""
    
    # User tables
    USERS = "users"
    
    # Summoner tables
    SUMMONERS = "summoners"
    USER_SUMMONERS = "user_summoners"
    
    # Match tables
    MATCHES = "matches"
    MATCH_PARTICIPANTS = "match_participants"
    
    # Champion tables
    CHAMPIONS = "champions"
    CHAMPION_STATS = "champion_stats"
    
    # Analytics tables
    PLAYER_ANALYTICS = "player_analytics"
    SKILL_PROGRESSION = "skill_progression"
    
    def __str__(self) -> str:
        """Return the string value when converted to string"""
        return self.value


class QueueType(str, Enum):
    """Enum for ranked queue types"""
    RANKED_SOLO_5x5 = "RANKED_SOLO_5x5"
    RANKED_FLEX_SR = "RANKED_FLEX_SR"
    RANKED_FLEX_TT = "RANKED_FLEX_TT"  # Legacy
    
    def __str__(self) -> str:
        return self.value


class Tier(str, Enum):
    """Enum for ranked tiers"""
    IRON = "IRON"
    BRONZE = "BRONZE"
    SILVER = "SILVER"
    GOLD = "GOLD"
    PLATINUM = "PLATINUM"
    EMERALD = "EMERALD"
    DIAMOND = "DIAMOND"
    MASTER = "MASTER"
    GRANDMASTER = "GRANDMASTER"
    CHALLENGER = "CHALLENGER"
    
    def __str__(self) -> str:
        return self.value


class Rank(str, Enum):
    """Enum for ranked divisions"""
    I = "I"
    II = "II"
    III = "III"
    IV = "IV"
    
    def __str__(self) -> str:
        return self.value
