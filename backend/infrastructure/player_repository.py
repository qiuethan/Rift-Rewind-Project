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
        
        # Clean API key (remove whitespace)
        api_key = self.riot_api_key.strip() if self.riot_api_key else None
        
        if not api_key:
            logger.warning("No Riot API key configured - using demo mode")
            from datetime import datetime
            return SummonerResponse(
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
        
        try:
            import httpx
            from datetime import datetime
            
            # Map region to Riot's regional routing values
            region_map = {
                'americas': 'americas',
                'europe': 'europe',
                'asia': 'asia',
                'sea': 'sea',
                'NA1': 'americas',
                'BR1': 'americas',
                'LA1': 'americas',
                'LA2': 'americas',
                'EUW1': 'europe',
                'EUN1': 'europe',
                'TR1': 'europe',
                'RU': 'europe',
                'KR': 'asia',
                'JP1': 'asia',
                'OC1': 'sea'
            }
            routing_region = region_map.get(region, 'americas')
            
            # Step 1: Get PUUID from Riot Account API
            account_url = f"https://{routing_region}.api.riotgames.com/riot/account/v1/accounts/by-riot-id/{game_name}/{tag_line}"
            
            headers = {
                "X-Riot-Token": api_key,
                "Accept": "application/json"
            }
            
            # Debug logging
            logger.debug(f"Riot API Key present: {bool(api_key)}")
            logger.debug(f"Calling Riot API: {account_url}")
            
            async with httpx.AsyncClient() as client:
                account_response = await client.get(account_url, headers=headers)
                
                if account_response.status_code != 200:
                    logger.error(f"Riot API error: {account_response.status_code} - {account_response.text}")
                    return None
                
                account_data = account_response.json()
                puuid = account_data.get('puuid')
                
                if not puuid:
                    logger.error("No PUUID in Riot API response")
                    return None
                
                logger.info(f"Retrieved PUUID: {puuid}")
                
                # Step 2: Get summoner details from Summoner API
                # SUMMONER-V4 uses platform-specific regions (na1, euw1, etc.), not routing regions
                # Map routing regions back to platform regions
                routing_to_platform = {
                    'americas': 'na1',  # Default to NA1 for americas
                    'europe': 'euw1',   # Default to EUW1 for europe
                    'asia': 'kr',       # Default to KR for asia
                    'sea': 'oc1'        # Default to OC1 for sea
                }
                
                # If region is already a platform region, use it; otherwise map from routing region
                if region in ['NA1', 'BR1', 'LA1', 'LA2', 'EUW1', 'EUN1', 'TR1', 'RU', 'KR', 'JP1', 'OC1']:
                    platform_region = region.lower()
                else:
                    platform_region = routing_to_platform.get(routing_region, 'na1')
                
                summoner_url = f"https://{platform_region}.api.riotgames.com/lol/summoner/v4/summoners/by-puuid/{puuid}"
                
                logger.debug(f"Calling Summoner API with platform region '{platform_region}': {summoner_url}")
                summoner_response = await client.get(summoner_url, headers=headers)
                logger.debug(f"Summoner API status code: {summoner_response.status_code}")
                
                if summoner_response.status_code != 200:
                    logger.error(f"Summoner API error: {summoner_response.status_code}")
                    logger.error(f"Summoner API response: {summoner_response.text}")
                    logger.warning(f"Using account data only - summoner level and icon will be 0")
                    # Return with just account data
                    return SummonerResponse(
                        id=puuid,
                        summoner_name=f"{game_name}#{tag_line}",
                        game_name=game_name,
                        tag_line=tag_line,
                        region=region,
                        puuid=puuid,
                        summoner_level=0,
                        profile_icon_id=0,
                        last_updated=datetime.utcnow().isoformat() + "Z"
                    )
                
                summoner_data = summoner_response.json()
                logger.debug(f"Summoner API response: {summoner_data}")
                
                # Combine data from both APIs
                response = SummonerResponse(
                    id=summoner_data.get('id', puuid),
                    summoner_name=f"{game_name}#{tag_line}",
                    game_name=game_name,
                    tag_line=tag_line,
                    region=region,
                    puuid=puuid,
                    summoner_level=summoner_data.get('summonerLevel', 0),
                    profile_icon_id=summoner_data.get('profileIconId', 0),
                    last_updated=datetime.utcnow().isoformat() + "Z"
                )
                
                logger.info(f"Successfully fetched summoner: {response.summoner_name} (Level {response.summoner_level}, Icon: {response.profile_icon_id})")
                logger.debug(f"Full response: {response}")
                return response
                
        except Exception as e:
            logger.error(f"Error fetching summoner from Riot API: {str(e)}")
            return None
    
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
        """Save summoner data and link to user (many-to-many)"""
        logger.info(f"Linking summoner to user: {user_id}")
        logger.debug(f"Summoner data: {summoner_data}")
        if self.client:
            puuid = summoner_data.get('puuid')
            
            # 1. Upsert summoner data (shared across all users)
            # UPSERT will update if exists (based on primary key 'puuid'), insert if not
            summoner_record = {
                'puuid': puuid,
                'summoner_name': summoner_data.get('summoner_name'),
                'game_name': summoner_data.get('game_name'),
                'tag_line': summoner_data.get('tag_line'),
                'region': summoner_data.get('region'),
                'summoner_level': summoner_data.get('summoner_level', 0),
                'profile_icon_id': summoner_data.get('profile_icon_id', 0),
                'last_updated': summoner_data.get('last_updated')
            }
            # Supabase upsert automatically uses primary key (puuid) for conflict resolution
            self.client.table('summoners').upsert(summoner_record).execute()
            logger.debug(f"Upserted summoner data for PUUID: {puuid}")
            
            # 2. Create/update user-summoner link (allows multiple users to link same account)
            # Check if link already exists first
            existing_link = self.client.table('user_summoners').select('id').eq('user_id', user_id).eq('puuid', puuid).execute()
            
            if existing_link.data and len(existing_link.data) > 0:
                # Link already exists, just log it
                logger.debug(f"User {user_id} already linked to summoner {puuid}")
            else:
                # Create new link
                link_record = {
                    'user_id': user_id,
                    'puuid': puuid
                }
                self.client.table('user_summoners').insert(link_record).execute()
                logger.debug(f"Created new user-summoner link for user {user_id}")
            
            logger.info(f"Successfully linked summoner {puuid} to user {user_id}")
            return SummonerResponse(**summoner_data)
        return None
    
    async def get_user_summoner(self, user_id: str) -> Optional[SummonerResponse]:
        """Get user's linked summoner (via junction table)"""
        logger.info(f"Fetching summoner for user: {user_id}")
        if self.client:
            # Join user_summoners with summoners to get full data
            response = self.client.table('user_summoners').select(
                'puuid, summoners(*)'
            ).eq('user_id', user_id).limit(1).execute()
            
            if response.data and len(response.data) > 0:
                link = response.data[0]
                summoner = link.get('summoners')
                if summoner:
                    logger.info(f"Found summoner: {summoner.get('summoner_name', 'N/A')}")
                    # Add id field (use puuid as id since summoners table doesn't have a separate id)
                    summoner['id'] = summoner.get('puuid')
                    return SummonerResponse(**summoner)
            
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
