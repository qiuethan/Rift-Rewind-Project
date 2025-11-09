"""
Dependency injection container
Factory functions for all services and repositories
"""
from config.supabase import supabase_service
from config.settings import settings
from config.riot_api import riot_api_config

# Domain
from domain.auth_domain import AuthDomain
from domain.player_domain import PlayerDomain
from domain.match_domain import MatchDomain
from domain.champion_domain import ChampionDomain
from domain.analytics_domain import AnalyticsDomain
from domain.riot_api_domain import RiotAPIDomain
from domain.champion_progress_domain import ChampionProgressDomain

# Repositories (Interfaces)
from repositories.auth_repository import AuthRepository
from repositories.player_repository import PlayerRepository
from repositories.match_repository import MatchRepository
from repositories.champion_repository import ChampionRepository
from repositories.analytics_repository import AnalyticsRepository
from repositories.riot_api_repository import RiotAPIRepository
from repositories.champion_progress_repository import ChampionProgressRepository

# Infrastructure (Implementations)
from infrastructure.auth_repository import AuthRepositorySupabase
from infrastructure.player_repository import PlayerRepositoryRiot
from infrastructure.match_repository import MatchRepositoryRiot
from infrastructure.champion_repository import ChampionRepositorySupabase
from infrastructure.analytics_repository import AnalyticsRepositorySupabase
from infrastructure.riot_api_repository import RiotAPIRepositoryImpl
from infrastructure.champion_progress_repository import ChampionProgressRepositorySupabase

# Services
from services.auth_service import AuthService
from services.player_service import PlayerService
from services.match_service import MatchService
from services.champion_service import ChampionService
from services.analytics_service import AnalyticsService
from services.llm_service import LLMService
from services.champion_progress_service import ChampionProgressService


# ============================================================================
# DOMAIN FACTORIES
# ============================================================================

def get_auth_domain() -> AuthDomain:
    """Factory for AuthDomain"""
    return AuthDomain()


def get_player_domain() -> PlayerDomain:
    """Factory for PlayerDomain"""
    return PlayerDomain()


def get_match_domain() -> MatchDomain:
    """Factory for MatchDomain"""
    return MatchDomain()


def get_champion_domain() -> ChampionDomain:
    """Factory for ChampionDomain"""
    return ChampionDomain()


def get_analytics_domain() -> AnalyticsDomain:
    """Factory for AnalyticsDomain"""
    return AnalyticsDomain()


def get_riot_api_domain() -> RiotAPIDomain:
    """Factory for RiotAPIDomain"""
    return RiotAPIDomain()


def get_champion_progress_domain() -> ChampionProgressDomain:
    """Factory for ChampionProgressDomain"""
    return ChampionProgressDomain()


# ============================================================================
# REPOSITORY FACTORIES (Infrastructure Implementations)
# ============================================================================

def get_riot_api_repository() -> RiotAPIRepository:
    """Factory for RiotAPIRepository"""
    if not riot_api_config:
        raise ValueError("Riot API configuration not initialized")
    return RiotAPIRepositoryImpl(riot_api_config)

def get_auth_repository() -> AuthRepository:
    """Factory for AuthRepository"""
    return AuthRepositorySupabase(supabase_service)


def get_player_repository() -> PlayerRepository:
    """Get player repository instance"""
    return PlayerRepositoryRiot(supabase_service, get_riot_api_repository())


def get_match_repository() -> MatchRepository:
    """Factory for MatchRepository"""
    return MatchRepositoryRiot(supabase_service, settings.RIOT_API_KEY)


def get_champion_repository() -> ChampionRepository:
    """Factory for ChampionRepository"""
    return ChampionRepositorySupabase(supabase_service, settings.OPENROUTER_API_KEY)


def get_analytics_repository() -> AnalyticsRepository:
    """Factory for AnalyticsRepository"""
    return AnalyticsRepositorySupabase(supabase_service, settings.OPENROUTER_API_KEY)


def get_champion_progress_repository() -> ChampionProgressRepository:
    """Factory for ChampionProgressRepository"""
    return ChampionProgressRepositorySupabase(supabase_service)


# ============================================================================
# SERVICE FACTORIES
# ============================================================================

def get_auth_service() -> AuthService:
    """Factory for AuthService"""
    return AuthService(
        auth_repository=get_auth_repository(),
        auth_domain=get_auth_domain()
    )


def get_player_service() -> PlayerService:
    """Factory for PlayerService"""
    return PlayerService(
        player_repository=get_player_repository(),
        player_domain=get_player_domain(),
        match_repository=get_match_repository(),
        riot_api_repository=get_riot_api_repository()
    )


def get_match_service() -> MatchService:
    """Factory for MatchService"""
    return MatchService(
        match_repository=get_match_repository(),
        match_domain=get_match_domain()
    )


def get_champion_service() -> ChampionService:
    """Factory for ChampionService"""
    return ChampionService(
        champion_repository=get_champion_repository(),
        player_repository=get_player_repository(),
        champion_domain=get_champion_domain()
    )


def get_analytics_service() -> AnalyticsService:
    """Factory for AnalyticsService"""
    return AnalyticsService(
        analytics_repository=get_analytics_repository(),
        match_repository=get_match_repository(),
        analytics_domain=get_analytics_domain()
    )


def get_bedrock_repository():
    """Factory for BedrockRepository"""
    from infrastructure.bedrock_repository import BedrockRepository
    return BedrockRepository()


def get_database():
    """Factory for Database client (returns Supabase client wrapper)"""
    from infrastructure.database.supabase_client import SupabaseClient
    return SupabaseClient(supabase_service)


def get_context_repository():
    """Factory for ContextRepository"""
    from infrastructure.context_repository import ContextRepositorySupabase
    return ContextRepositorySupabase(supabase_service)


def get_llm_service() -> LLMService:
    """Factory for LLMService with injected dependencies"""
    return LLMService(
        bedrock_repository=get_bedrock_repository(),
        context_repository=get_context_repository()
    )


# Alias for backward compatibility
def get_bedrock_service() -> LLMService:
    """Deprecated: Use get_llm_service instead"""
    return get_llm_service()


def get_champion_progress_service() -> ChampionProgressService:
    """Factory for ChampionProgressService"""
    return ChampionProgressService(
        champion_progress_repository=get_champion_progress_repository(),
        player_repository=get_player_repository(),
        champion_progress_domain=get_champion_progress_domain()
    )
