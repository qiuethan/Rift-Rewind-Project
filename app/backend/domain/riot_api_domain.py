"""
Riot API Domain - Business logic and validation for Riot API operations
"""
from domain.exceptions import DomainException


class RiotAPIDomain:
    """Domain logic for Riot API operations"""
    
    VALID_REGIONS = ['americas', 'europe', 'asia', 'sea', 'NA1', 'BR1', 'LA1', 'LA2', 
                     'EUW1', 'EUN1', 'TR1', 'RU', 'KR', 'JP1', 'OC1']
    
    def validate_region(self, region: str) -> None:
        """Validate region code"""
        if not region:
            raise DomainException("Region is required")
        
        if region not in self.VALID_REGIONS:
            raise DomainException(f"Invalid region: {region}. Must be one of {self.VALID_REGIONS}")
    
    def validate_puuid(self, puuid: str) -> None:
        """Validate PUUID format"""
        if not puuid:
            raise DomainException("PUUID is required")
        
        if not isinstance(puuid, str) or len(puuid) < 10:
            raise DomainException("Invalid PUUID format")
    
    def validate_summoner_id(self, summoner_id: str) -> None:
        """Validate summoner ID"""
        if not summoner_id:
            raise DomainException("Summoner ID is required")
        
        if not isinstance(summoner_id, str):
            raise DomainException("Invalid summoner ID format")
    
    def validate_riot_id(self, game_name: str, tag_line: str) -> None:
        """Validate Riot ID (game_name#tag_line)"""
        if not game_name or not tag_line:
            raise DomainException("Both game name and tag line are required")
        
        if not isinstance(game_name, str) or not isinstance(tag_line, str):
            raise DomainException("Game name and tag line must be strings")
        
        if len(game_name) < 3 or len(game_name) > 16:
            raise DomainException("Game name must be between 3 and 16 characters")
        
        if len(tag_line) < 3 or len(tag_line) > 5:
            raise DomainException("Tag line must be between 3 and 5 characters")
    
    def validate_champion_id(self, champion_id: int) -> None:
        """Validate champion ID"""
        if not champion_id:
            raise DomainException("Champion ID is required")
        
        if not isinstance(champion_id, int) or champion_id < 1:
            raise DomainException("Invalid champion ID")
    
    def validate_count(self, count: int, max_count: int = 100) -> None:
        """Validate count parameter"""
        if not isinstance(count, int) or count < 1:
            raise DomainException("Count must be a positive integer")
        
        if count > max_count:
            raise DomainException(f"Count cannot exceed {max_count}")
