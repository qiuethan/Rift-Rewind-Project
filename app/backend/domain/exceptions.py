"""
Domain exceptions - Pure business rule violations
These are framework-agnostic and can be caught/translated by services
"""


class DomainException(Exception):
    """Base exception for domain violations"""
    def __init__(self, message: str):
        self.message = message
        super().__init__(self.message)


class ValidationError(DomainException):
    """Validation rule violation"""
    pass


class InvalidEmailError(ValidationError):
    """Invalid email format"""
    pass


class InvalidPasswordError(ValidationError):
    """Invalid password"""
    pass


class InvalidRegionError(ValidationError):
    """Invalid region"""
    pass


class InvalidSummonerNameError(ValidationError):
    """Invalid summoner name"""
    pass


class InvalidMatchIdError(ValidationError):
    """Invalid match ID"""
    pass


class InvalidChampionIdError(ValidationError):
    """Invalid champion ID"""
    pass


class InvalidTimeRangeError(ValidationError):
    """Invalid time range"""
    pass
