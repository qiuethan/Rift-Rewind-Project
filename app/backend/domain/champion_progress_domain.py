"""
Champion Progress Domain - Pure business logic
Following Clean Architecture: No external dependencies, framework-agnostic
"""
from domain.exceptions import ValidationError, InvalidChampionIdError


class ChampionProgressDomain:
    """Business rules for champion progress tracking"""
    
    def validate_champion_id(self, champion_id: int) -> None:
        """
        Validate champion ID is positive
        
        Raises:
            InvalidChampionIdError: If champion ID is invalid
        """
        if champion_id <= 0:
            raise InvalidChampionIdError(f"Champion ID must be positive, got: {champion_id}")
    
    def validate_limit(self, limit: int) -> None:
        """
        Validate limit for match history
        
        Raises:
            ValidationError: If limit is out of bounds
        """
        if limit < 1:
            raise ValidationError("Limit must be at least 1")
        if limit > 100:
            raise ValidationError("Limit cannot exceed 100")
    
    def validate_score(self, score: float, score_name: str) -> None:
        """
        Validate performance score is non-negative
        
        Raises:
            ValidationError: If score is negative
        """
        if score < 0:
            raise ValidationError(f"{score_name} cannot be negative, got: {score}")
    
    def validate_kda_components(self, kills: int, deaths: int, assists: int) -> None:
        """
        Validate KDA components are non-negative
        
        Raises:
            ValidationError: If any component is negative
        """
        if kills < 0:
            raise ValidationError(f"Kills cannot be negative, got: {kills}")
        if deaths < 0:
            raise ValidationError(f"Deaths cannot be negative, got: {deaths}")
        if assists < 0:
            raise ValidationError(f"Assists cannot be negative, got: {assists}")
    
    def calculate_kda(self, kills: int, deaths: int, assists: int) -> float:
        """
        Calculate KDA ratio
        Pure calculation: (K + A) / D, with D defaulting to 1 if 0
        
        Args:
            kills: Number of kills
            deaths: Number of deaths
            assists: Number of assists
            
        Returns:
            KDA ratio rounded to 2 decimal places
        """
        divisor = max(deaths, 1)  # Avoid division by zero
        return round((kills + assists) / divisor, 2)
    
    def calculate_win_rate(self, wins: int, losses: int) -> float:
        """
        Calculate win rate percentage
        
        Args:
            wins: Number of wins
            losses: Number of losses
            
        Returns:
            Win rate as percentage (0-100) rounded to 2 decimal places
        """
        total = wins + losses
        if total == 0:
            return 0.0
        return round((wins / total) * 100, 2)
    
    def determine_trend(self, recent_scores: list[float], window_size: int = 5) -> str:
        """
        Determine performance trend based on recent scores
        
        Args:
            recent_scores: List of recent performance scores (newest first)
            window_size: Number of games to consider for trend
            
        Returns:
            'improving', 'declining', or 'stable'
        """
        if len(recent_scores) < window_size:
            return "stable"
        
        # Take the most recent games
        recent = recent_scores[:window_size]
        
        # Compare first half vs second half
        mid = window_size // 2
        first_half_avg = sum(recent[mid:]) / (window_size - mid)
        second_half_avg = sum(recent[:mid]) / mid
        
        # Calculate percentage difference
        if first_half_avg == 0:
            return "stable"
        
        diff_percentage = ((second_half_avg - first_half_avg) / first_half_avg) * 100
        
        if diff_percentage > 5:
            return "improving"
        elif diff_percentage < -5:
            return "declining"
        else:
            return "stable"
    
    def calculate_average_score(self, scores: list[float]) -> float:
        """
        Calculate average score from a list
        
        Args:
            scores: List of scores
            
        Returns:
            Average score rounded to 2 decimal places
        """
        if not scores:
            return 0.0
        return round(sum(scores) / len(scores), 2)
    
    def validate_trend_value(self, trend: str) -> None:
        """
        Validate trend value is one of the allowed values
        
        Raises:
            ValidationError: If trend is invalid
        """
        valid_trends = ["improving", "declining", "stable"]
        if trend not in valid_trends:
            raise ValidationError(f"Trend must be one of {valid_trends}, got: {trend}")
