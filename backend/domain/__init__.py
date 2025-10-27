"""Domain module exports"""
from domain.auth_domain import AuthDomain
from domain.player_domain import PlayerDomain
from domain.match_domain import MatchDomain
from domain.champion_domain import ChampionDomain
from domain.analytics_domain import AnalyticsDomain

__all__ = [
    'AuthDomain',
    'PlayerDomain',
    'MatchDomain',
    'ChampionDomain',
    'AnalyticsDomain',
]
