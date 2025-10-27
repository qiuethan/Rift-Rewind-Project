"""Dependency injection module exports"""
from dependency.dependencies import (
    get_auth_service,
    get_player_service,
    get_match_service,
    get_champion_service,
    get_analytics_service
)

__all__ = [
    'get_auth_service',
    'get_player_service',
    'get_match_service',
    'get_champion_service',
    'get_analytics_service',
]
