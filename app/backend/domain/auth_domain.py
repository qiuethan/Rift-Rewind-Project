"""
Authentication domain - Pure business logic for auth
"""
from domain.exceptions import InvalidEmailError, InvalidPasswordError, InvalidSummonerNameError, InvalidRegionError
import re


class AuthDomain:
    """Pure business logic for authentication"""
    
    def __init__(self):
        pass
    
    def validate_email(self, email: str) -> None:
        """Validate email format business rules"""
        if not email or len(email) < 5:
            raise InvalidEmailError("Email must be at least 5 characters")
        
        email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        if not re.match(email_pattern, email):
            raise InvalidEmailError("Invalid email format")
    
    def validate_password(self, password: str) -> None:
        """Validate password strength business rules"""
        if not password or len(password) < 8:
            raise InvalidPasswordError("Password must be at least 8 characters")
        
        if len(password) > 100:
            raise InvalidPasswordError("Password must be less than 100 characters")
        
        # Check for at least one number
        if not any(char.isdigit() for char in password):
            raise InvalidPasswordError("Password must contain at least one number")
        
        # Check for at least one letter
        if not any(char.isalpha() for char in password):
            raise InvalidPasswordError("Password must contain at least one letter")
    
    def validate_summoner_name(self, summoner_name: str) -> None:
        """Validate summoner name business rules"""
        if not summoner_name:
            return  # Optional field
        
        if len(summoner_name) < 3 or len(summoner_name) > 16:
            raise InvalidSummonerNameError("Summoner name must be between 3 and 16 characters")
    
    def validate_region(self, region: str) -> None:
        """Validate region business rules"""
        if not region:
            return  # Optional field
        
        valid_regions = ["NA1", "EUW1", "EUN1", "KR", "BR1", "JP1", "LA1", "LA2", "OC1", "TR1", "RU"]
        if region not in valid_regions:
            raise InvalidRegionError(f"Region must be one of: {', '.join(valid_regions)}")
