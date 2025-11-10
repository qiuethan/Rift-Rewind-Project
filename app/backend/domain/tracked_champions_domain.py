"""
Tracked Champions Domain
Business logic for champion tracking
"""
from domain.exceptions import ValidationError


class MaxTrackedChampionsError(ValidationError):
    """User has reached maximum tracked champions limit"""
    pass


class ChampionAlreadyTrackedError(ValidationError):
    """Champion is already being tracked"""
    pass


class ChampionNotTrackedError(ValidationError):
    """Champion is not in tracked list"""
    pass


class TrackedChampionsDomain:
    """Business rules for champion tracking"""
    
    MAX_TRACKED_CHAMPIONS = 5
    
    def validate_champion_id(self, champion_id: int) -> None:
        """
        Validate champion ID is positive
        
        Args:
            champion_id: Champion ID to validate
            
        Raises:
            ValidationError: If champion ID is invalid
        """
        if champion_id <= 0:
            raise ValidationError("Champion ID must be a positive integer")
    
    def validate_tracking_limit(self, current_count: int) -> None:
        """
        Validate user hasn't exceeded tracking limit
        
        Args:
            current_count: Current number of tracked champions
            
        Raises:
            MaxTrackedChampionsError: If limit is reached
        """
        if current_count >= self.MAX_TRACKED_CHAMPIONS:
            raise MaxTrackedChampionsError(
                f"Maximum of {self.MAX_TRACKED_CHAMPIONS} champions can be tracked"
            )
    
    def validate_not_already_tracked(self, champion_id: int, tracked_ids: list) -> None:
        """
        Validate champion is not already tracked
        
        Args:
            champion_id: Champion ID to check
            tracked_ids: List of currently tracked champion IDs
            
        Raises:
            ChampionAlreadyTrackedError: If champion is already tracked
        """
        if champion_id in tracked_ids:
            raise ChampionAlreadyTrackedError("Champion is already being tracked")
    
    def validate_is_tracked(self, champion_id: int, tracked_ids: list) -> None:
        """
        Validate champion is currently tracked
        
        Args:
            champion_id: Champion ID to check
            tracked_ids: List of currently tracked champion IDs
            
        Raises:
            ChampionNotTrackedError: If champion is not tracked
        """
        if champion_id not in tracked_ids:
            raise ChampionNotTrackedError("Champion is not in tracked list")
