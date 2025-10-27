"""
Riot API Repository Implementation
"""
from repositories.riot_api_repository import RiotAPIRepository
from config.riot_api import RiotAPIConfig
from models.riot_api import (
    AccountResponse,
    SummonerAPIResponse,
    LeagueEntryResponse,
    ChampionMasteryResponse
)
from typing import Optional, List, Dict, Any
from utils.logger import logger


class RiotAPIRepositoryImpl(RiotAPIRepository):
    """Implementation of Riot API repository using RiotAPIConfig"""
    
    def __init__(self, riot_config: RiotAPIConfig):
        """
        Initialize with Riot API configuration
        
        Args:
            riot_config: Configured Riot API client
        """
        self.riot = riot_config
        logger.info("Riot API repository initialized")
    
    # ============================================================================
    # ACCOUNT API
    # ============================================================================
    
    async def get_account_by_riot_id(self, game_name: str, tag_line: str, region: str) -> Optional[Dict[str, Any]]:
        """Get account by Riot ID"""
        logger.info(f"Fetching account: {game_name}#{tag_line} in {region}")
        url = f"{self.riot.ACCOUNT_API_BASE.format(region=region)}/riot/account/v1/accounts/by-riot-id/{game_name}/{tag_line}"
        return await self.riot.request(url, "Account API")
    
    # ============================================================================
    # SUMMONER API
    # ============================================================================
    
    async def get_summoner_by_puuid(self, puuid: str, region: str) -> Optional[Dict[str, Any]]:
        """Get summoner by PUUID"""
        logger.info(f"Fetching summoner by PUUID: {puuid}")
        platform_region = self.riot.get_platform_region(region)
        url = f"{self.riot.SUMMONER_API_BASE.format(region=platform_region)}/lol/summoner/v4/summoners/by-puuid/{puuid}"
        return await self.riot.request(url, "Summoner API")
    
    # ============================================================================
    # LEAGUE API (Ranked)
    # ============================================================================
    
    async def get_league_entries_by_summoner(self, summoner_id: str, region: str) -> List[Dict[str, Any]]:
        """Get ranked league entries for summoner by encrypted summoner ID"""
        logger.info(f"Fetching league entries for summoner: {summoner_id}")
        platform_region = self.riot.get_platform_region(region)
        url = f"{self.riot.LEAGUE_API_BASE.format(region=platform_region)}/lol/league/v4/entries/by-summoner/{summoner_id}"
        result = await self.riot.request(url, "League API")
        return result if result else []
    
    async def get_league_entries_by_puuid(self, puuid: str, region: str) -> List[Dict[str, Any]]:
        """
        Get ranked league entries for summoner by PUUID
        Note: 'encryptedSummonerId' in Riot API docs refers to the PUUID itself
        """
        logger.info(f"Fetching league entries for PUUID: {puuid}")
        
        # Use the standard League API v4 endpoint with PUUID (encryptedSummonerId = PUUID)
        platform_region = self.riot.get_platform_region(region)
        url = f"{self.riot.LEAGUE_API_BASE.format(region=platform_region)}/lol/league/v4/entries/by-summoner/{puuid}"
        
        logger.debug(f"Calling League API: {url}")
        result = await self.riot.request(url, "League API")
        
        if result:
            logger.info(f"Successfully fetched {len(result)} league entries")
            return result
        
        logger.info("No league entries found - account is unranked")
        return []
    
    # ============================================================================
    # MATCH API v5
    # ============================================================================
    
    async def get_match_ids_by_puuid(self, puuid: str, region: str, count: int = 10, start: int = 0) -> List[str]:
        """Get list of match IDs for a player with pagination"""
        logger.info(f"Fetching {count} match IDs for PUUID: {puuid} (starting at {start})")
        
        # Match API uses regional routing (americas, europe, asia, sea)
        url = f"{self.riot.ACCOUNT_API_BASE.format(region=region)}/lol/match/v5/matches/by-puuid/{puuid}/ids?count={count}&start={start}"
        
        logger.debug(f"Calling Match API: {url}")
        result = await self.riot.request(url, "Match API")
        
        if result:
            logger.info(f"Retrieved {len(result)} match IDs")
            return result
        
        logger.warning("No match history found")
        return []
    
    async def get_match_details(self, match_id: str, region: str) -> Optional[Dict[str, Any]]:
        """Get detailed match data by match ID"""
        logger.info(f"Fetching match details for: {match_id}")
        
        url = f"{self.riot.ACCOUNT_API_BASE.format(region=region)}/lol/match/v5/matches/{match_id}"
        
        logger.debug(f"Calling Match Details API: {url}")
        result = await self.riot.request(url, "Match Details API")
        
        if result:
            logger.info(f"Successfully retrieved match details for {match_id}")
            return result
        
        logger.warning(f"Could not retrieve match details for {match_id}")
        return None
    
    # ============================================================================
    # CHAMPION MASTERY API
    # ============================================================================
    
    async def get_champion_masteries(self, puuid: str, region: str) -> List[Dict[str, Any]]:
        """Get all champion masteries for summoner"""
        logger.info(f"Fetching all champion masteries for PUUID: {puuid}")
        platform_region = self.riot.get_platform_region(region)
        url = f"{self.riot.MASTERY_API_BASE.format(region=platform_region)}/lol/champion-mastery/v4/champion-masteries/by-puuid/{puuid}"
        result = await self.riot.request(url, "Champion Mastery API")
        return result if result else []
    
    async def get_top_champion_masteries(self, puuid: str, region: str, count: int) -> List[Dict[str, Any]]:
        """Get top N champion masteries"""
        logger.info(f"Fetching top {count} champion masteries for PUUID: {puuid}")
        
        platform_region = self.riot.get_platform_region(region)
        url = f"{self.riot.MASTERY_API_BASE.format(region=platform_region)}/lol/champion-mastery/v4/champion-masteries/by-puuid/{puuid}/top?count={count}"
        
        result = await self.riot.request(url, "Top Champion Mastery API")
        return result if result else []
    
    async def get_mastery_score(self, puuid: str, region: str) -> Optional[int]:
        """Get total mastery score"""
        logger.info(f"Fetching mastery score for PUUID: {puuid}")
        
        platform_region = self.riot.get_platform_region(region)
        url = f"{self.riot.MASTERY_API_BASE.format(region=platform_region)}/lol/champion-mastery/v4/scores/by-puuid/{puuid}"
        
        return await self.riot.request(url, "Mastery Score API")
    
    async def get_champion_mastery_by_champion(self, puuid: str, champion_id: int, region: str) -> Optional[Dict[str, Any]]:
        """Get mastery for specific champion"""
        logger.info(f"Fetching mastery for champion {champion_id}, PUUID: {puuid}")
        
        platform_region = self.riot.get_platform_region(region)
        url = f"{self.riot.MASTERY_API_BASE.format(region=platform_region)}/lol/champion-mastery/v4/champion-masteries/by-puuid/{puuid}/by-champion/{champion_id}"
        
        return await self.riot.request(url, f"Champion {champion_id} Mastery API")
