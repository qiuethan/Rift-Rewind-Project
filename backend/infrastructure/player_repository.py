"""
Player repository implementation with Riot API
"""
from repositories.player_repository import PlayerRepository
from models.players import SummonerResponse, PlayerStatsResponse
from infrastructure.database.database_client import DatabaseClient
from typing import Optional, List
from utils.logger import logger


class PlayerRepositoryRiot(PlayerRepository):
    """Riot API + Database implementation of player repository"""
    
    def __init__(self, client: DatabaseClient, riot_api_key: str):
        self.client = client
        self.riot_api_key = riot_api_key
    
    async def get_summoner_by_name(self, summoner_name: str, region: str) -> Optional[SummonerResponse]:
        """Get summoner data by name from Riot API (DEMO)"""
        # Demo implementation - would call Riot API
        return SummonerResponse(
            id=f"demo_summoner_{summoner_name}",
            summoner_name=summoner_name,
            region=region,
            puuid=f"demo_puuid_{summoner_name}",
            summoner_level=100,
            profile_icon_id=1,
            last_updated="2024-01-01T00:00:00Z"
        )
    
    async def get_summoner_by_riot_id(self, game_name: str, tag_line: str, region: str) -> Optional[SummonerResponse]:
        """Get summoner data by Riot ID from Riot API"""
        logger.info(f"Fetching summoner by Riot ID: {game_name}#{tag_line} ({region})")
        
        # For now, demo implementation
        # In production, this would call:
        # 1. ACCOUNT-V1 API: /riot/account/v1/accounts/by-riot-id/{gameName}/{tagLine}
        # 2. Get PUUID from response
        # 3. SUMMONER-V4 API: /lol/summoner/v4/summoners/by-puuid/{encryptedPUUID}
        
        from datetime import datetime
        
        response = SummonerResponse(
            id=f"demo_summoner_{game_name}",
            summoner_name=f"{game_name}#{tag_line}",
            game_name=game_name,
            tag_line=tag_line,
            region=region,
            puuid=f"demo_puuid_{game_name}_{tag_line}",
            summoner_level=100,
            profile_icon_id=1,
            last_updated=datetime.utcnow().isoformat() + "Z"
        )
        logger.debug(f"Created demo summoner: {response.summoner_name} (PUUID: {response.puuid})")
        return response
    
    async def get_summoner_by_puuid(self, puuid: str) -> Optional[SummonerResponse]:
        """Get summoner data by PUUID from Riot API (DEMO)"""
        # Demo implementation
        return SummonerResponse(
            id=f"demo_summoner_id",
            summoner_name="DemoSummoner",
            region="NA1",
            puuid=puuid,
            summoner_level=100,
            profile_icon_id=1,
            last_updated="2024-01-01T00:00:00Z"
        )
    
    async def save_summoner(self, user_id: str, summoner_data: dict) -> Optional[SummonerResponse]:
        """Save summoner data to Supabase"""
        logger.info(f"Saving summoner for user: {user_id}")
        logger.debug(f"Summoner data: {summoner_data}")
        if self.client:
            summoner_data['user_id'] = user_id
            result = self.client.table('summoners').upsert(summoner_data).execute()
            logger.info(f"Successfully saved summoner to Supabase")
            return SummonerResponse(**summoner_data)
        return None
    
    async def get_user_summoner(self, user_id: str) -> Optional[SummonerResponse]:
        """Get user's linked summoner from Supabase"""
        logger.info(f"Fetching summoner for user: {user_id}")
        if self.client:
            response = self.client.table('summoners').select('*').eq('user_id', user_id).limit(1).execute()
            if response.data:
                logger.info(f"Found summoner: {response.data[0].get('summoner_name', 'N/A')}")
                return SummonerResponse(**response.data[0])
            else:
                logger.info(f"No summoner found for user")
        return None
    
    async def get_player_stats(self, summoner_id: str) -> Optional[PlayerStatsResponse]:
        """Get player statistics (DEMO)"""
        # Demo implementation
        return PlayerStatsResponse(
            summoner_id=summoner_id,
            total_games=100,
            wins=55,
            losses=45,
            win_rate=55.0,
            favorite_champions=["Ahri", "Lux", "Syndra"],
            average_kda=3.2,
            average_cs_per_min=7.5
        )
    
    async def get_match_history(self, puuid: str, count: int) -> List[str]:
        """Get match history for a player (DEMO)"""
        # Demo implementation
        return [f"NA1_demo_match_{i}" for i in range(count)]
