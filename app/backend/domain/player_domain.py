"""
Player domain - Pure business logic for player operations
"""
from domain.exceptions import InvalidSummonerNameError, InvalidRegionError, ValidationError


class PlayerDomain:
    """Pure business logic for player operations"""
    
    def __init__(self):
        pass
    
    def validate_summoner_name(self, summoner_name: str) -> None:
        """Validate summoner name business rules"""
        if not summoner_name or len(summoner_name.strip()) < 3:
            raise InvalidSummonerNameError("Summoner name must be at least 3 characters")
        
        if len(summoner_name) > 16:
            raise InvalidSummonerNameError("Summoner name must be less than 16 characters")
    
    def validate_region(self, region: str) -> None:
        """Validate region business rules"""
        valid_regions = ["americas", "europe", "asia", "sea", "NA1", "EUW1", "EUN1", "KR", "BR1", "JP1", "LA1", "LA2", "OC1", "TR1", "RU"]
        if region not in valid_regions:
            raise InvalidRegionError(f"Region must be one of: {', '.join(valid_regions)}")
    
    def calculate_win_rate(self, wins: int, losses: int) -> float:
        """Calculate win rate percentage"""
        total_games = wins + losses
        if total_games == 0:
            return 0.0
        return round((wins / total_games) * 100, 2)
    
    def calculate_kda(self, kills: int, deaths: int, assists: int) -> float:
        """Calculate KDA ratio"""
        if deaths == 0:
            return float(kills + assists)
        return round((kills + assists) / deaths, 2)
    
    def validate_puuid(self, puuid: str) -> None:
        """Validate PUUID format"""
        if not puuid or len(puuid) < 10:
            raise ValidationError("Invalid PUUID format")
