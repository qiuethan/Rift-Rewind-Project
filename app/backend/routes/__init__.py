"""Routes module exports"""
from routes.auth import router as auth_router
from routes.players import router as players_router
from routes.matches import router as matches_router
from routes.champions import router as champions_router
from routes.analytics import router as analytics_router
from routes.health import router as health_router
from routes.champion_progress import router as champion_progress_router
from routes.llm import router as llm_router

__all__ = [
    'auth_router',
    'players_router',
    'matches_router',
    'champions_router',
    'analytics_router',
    'health_router',
    'champion_progress_router',
    'llm_router',
]
