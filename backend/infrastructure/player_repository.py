"""
Player repository implementation with Riot API
"""
from repositories.player_repository import PlayerRepository
from repositories.riot_api_repository import RiotAPIRepository
from models.players import SummonerResponse, PlayerStatsResponse, SummonerRecord
from models.riot_api import RankedData, MasteryData, ChampionMasteryResponse, MatchHistoryResponse
from infrastructure.database.database_client import DatabaseClient
from constants.database import DatabaseTable
from typing import Optional, List
from utils.logger import logger
from datetime import datetime


class PlayerRepositoryRiot(PlayerRepository):
    """Riot API + Database implementation of player repository"""
    
    def __init__(self, db: DatabaseClient, riot_api: RiotAPIRepository):
        """
        Initialize repository with injected dependencies
        
        Args:
            db: Database abstraction for data persistence
            riot_api: Riot API repository for external API calls
        """
        self.db = db
        self.riot_api = riot_api
        logger.info("Player repository initialized with Riot API")
    
    async def get_summoner_by_name(self, summoner_name: str, region: str) -> Optional[SummonerResponse]:
        """
        DEPRECATED: Riot API no longer supports summoner lookup by name alone.
        Use get_summoner_by_riot_id() instead with game_name#tag_line format.
        """
        logger.error("get_summoner_by_name is deprecated - use get_summoner_by_riot_id instead")
        raise NotImplementedError("Summoner lookup by name is deprecated. Use Riot ID (game_name#tag_line) instead.")
    
    async def get_summoner_by_riot_id(self, game_name: str, tag_line: str, region: str) -> Optional[SummonerResponse]:
        """
        Get basic summoner data by Riot ID from Riot API
        
        Fetches basic summoner info (name, level, icon, puuid) only.
        Ranked and mastery data must be fetched separately.
        """
        logger.info(f"Fetching summoner by Riot ID: {game_name}#{tag_line} in {region}")
        
        try:
            # Step 1: Get account (PUUID) from Riot ID
            account_data = await self.riot_api.get_account_by_riot_id(game_name, tag_line, region)
            if not account_data:
                logger.warning(f"Account not found: {game_name}#{tag_line}")
                return None
            
            puuid = account_data.get('puuid')
            if not puuid:
                logger.error("No PUUID in account response")
                return None
            
            # Step 2: Get summoner data by PUUID
            summoner_data = await self.riot_api.get_summoner_by_puuid(puuid, region)
            if not summoner_data:
                logger.warning(f"Summoner not found for PUUID: {puuid}")
                return None
            
            # Extract encrypted summoner ID if available (needed for ranked API)
            summoner_id = summoner_data.get('id', puuid)
            logger.debug(f"Summoner ID for ranked lookups: {summoner_id}")
            
            response = SummonerResponse(
                id=summoner_id,
                summoner_name=f"{game_name}#{tag_line}",
                game_name=game_name,
                tag_line=tag_line,
                region=region,
                puuid=puuid,
                summoner_level=summoner_data.get('summonerLevel', 0),
                profile_icon_id=summoner_data.get('profileIconId', 0),
                last_updated=datetime.utcnow().isoformat() + "Z"
            )
            
            logger.info(f"Successfully fetched summoner: {response.summoner_name} (Level {response.summoner_level})")
            return response
            
        except Exception as e:
            logger.error(f"Error fetching summoner from Riot API: {str(e)}")
            return None
    
    async def get_summoner_by_puuid(self, puuid: str, region: str = 'americas') -> Optional[SummonerResponse]:
        """Get complete summoner data by PUUID including ranked and mastery information"""
        logger.info(f"Fetching summoner by PUUID: {puuid}")
        
        try:
            summoner_data = await self.riot_api.get_summoner_by_puuid(puuid, region)
            if not summoner_data:
                logger.warning(f"Summoner not found for PUUID: {puuid}")
                return None
            
            logger.debug(f"Summoner data keys: {summoner_data.keys()}")
            
            # Get summoner name from database if available (Riot API no longer returns it)
            db_summoner = await self.get_user_summoner_from_db(puuid)
            summoner_name = db_summoner.get('summoner_name') if db_summoner else 'Unknown'
            game_name = db_summoner.get('game_name') if db_summoner else None
            tag_line = db_summoner.get('tag_line') if db_summoner else None
            
            logger.debug(f"Using summoner name from DB: {summoner_name}")
            
            ranked_data = await self.get_ranked_data_by_puuid(puuid, region)
            logger.debug(f"Ranked data: Solo={ranked_data.ranked_solo_tier}, Flex={ranked_data.ranked_flex_tier}")
            
            mastery_data = await self.get_mastery_data(puuid, region)
            logger.debug(f"Mastery data: {len(mastery_data.champion_masteries)} masteries, score={mastery_data.total_mastery_score}")
            
            response = SummonerResponse(
                id=summoner_data.get('id', puuid),
                summoner_name=summoner_name,
                game_name=game_name,
                tag_line=tag_line,
                puuid=puuid,
                region=region,
                summoner_level=summoner_data.get('summonerLevel', 0),
                profile_icon_id=summoner_data.get('profileIconId', 0),
                last_updated=datetime.utcnow().isoformat() + "Z",
                **ranked_data.dict(),
                **mastery_data.dict()
            )
            
            logger.info(f"Successfully fetched summoner by PUUID: {response.summoner_name} (Level {response.summoner_level}), Masteries: {len(response.champion_masteries) if response.champion_masteries else 0}")
            return response
            
        except Exception as e:
            logger.error(f"Error fetching summoner by PUUID: {str(e)}")
            return None
    
    async def get_ranked_data_by_puuid(self, puuid: str, region: str) -> RankedData:
        """
        Fetch ranked data for a summoner by PUUID from Riot League API
        
        Args:
            puuid: Player UUID
            region: Region code
            
        Returns:
            RankedData model with ranked solo and flex queue data
        """
        if not puuid:
            logger.warning("No PUUID provided for ranked data fetch")
            return RankedData()
        
        try:
            league_entries = await self.riot_api.get_league_entries_by_puuid(puuid, region)
            logger.info(f"League API returned {len(league_entries)} ranked entries")
            
            if not league_entries:
                logger.info("Account is unranked (no ranked games this season)")
                return RankedData()
            
            ranked_data = RankedData.from_dict_entries(league_entries)
            
            if ranked_data.ranked_solo_tier:
                logger.info(f"Found Solo/Duo rank: {ranked_data.ranked_solo_tier} {ranked_data.ranked_solo_rank} ({ranked_data.ranked_solo_lp} LP)")
            if ranked_data.ranked_flex_tier:
                logger.info(f"Found Flex rank: {ranked_data.ranked_flex_tier} {ranked_data.ranked_flex_rank}")
            
            if not ranked_data.ranked_solo_tier and not ranked_data.ranked_flex_tier:
                logger.info("No ranked data found - account is unranked")
            
            return ranked_data
                
        except Exception as e:
            logger.error(f"Error fetching ranked data: {str(e)}")
            return RankedData()
    
    async def get_ranked_data(self, summoner_id: str, region: str) -> RankedData:
        """
        Fetch ranked data for a summoner from Riot League API
        
        Args:
            summoner_id: Encrypted summoner ID
            region: Region code
            
        Returns:
            RankedData model with ranked solo and flex queue data
        """
        if not summoner_id:
            logger.warning("No summoner_id provided for ranked data fetch")
            return RankedData()
        
        try:
            league_entries = await self.riot_api.get_league_entries_by_summoner(summoner_id, region)
            logger.info(f"League API returned {len(league_entries)} ranked entries")
            
            if not league_entries:
                logger.info("Account is unranked (no ranked games this season)")
                return RankedData()
            
            ranked_data = RankedData.from_dict_entries(league_entries)
            
            if ranked_data.ranked_solo_tier:
                logger.info(f"Found Solo/Duo rank: {ranked_data.ranked_solo_tier} {ranked_data.ranked_solo_rank} ({ranked_data.ranked_solo_lp} LP)")
            if ranked_data.ranked_flex_tier:
                logger.info(f"Found Flex rank: {ranked_data.ranked_flex_tier} {ranked_data.ranked_flex_rank}")
            
            if not ranked_data.ranked_solo_tier and not ranked_data.ranked_flex_tier:
                logger.info("No ranked data found - account is unranked")
            
            return ranked_data
                
        except Exception as e:
            logger.error(f"Error fetching ranked data: {str(e)}")
            return RankedData()
    
    async def get_mastery_data(self, puuid: str, region: str) -> MasteryData:
        """
        Fetch champion mastery data for a summoner from Riot API
        
        Args:
            puuid: Player UUID
            region: Region code
            
        Returns:
            MasteryData model with champion masteries, top champions, and total mastery score
        """
        try:
            logger.info(f"Fetching champion mastery data for PUUID: {puuid}")
            
            all_masteries = await self.riot_api.get_champion_masteries(puuid, region)
            mastery_score = await self.riot_api.get_mastery_score(puuid, region)
            
            if all_masteries:
                logger.info(f"Retrieved {len(all_masteries)} champion masteries")
            if mastery_score is not None:
                logger.info(f"Retrieved mastery score: {mastery_score}")
            
            return MasteryData.from_api_data(all_masteries or [], mastery_score)
            
        except Exception as e:
            logger.warning(f"Error fetching mastery data (non-critical): {str(e)}")
            return MasteryData()
    
    async def save_summoner(self, user_id: str, summoner_data: dict) -> Optional[SummonerResponse]:
        """
        Save summoner data to database and link to user
        
        Handles database persistence only. Does not fetch from Riot API.
        
        Args:
            user_id: User ID to link summoner to
            summoner_data: Complete summoner data dictionary
            
        Returns:
            SummonerResponse with saved data
        """
        logger.info(f"Saving summoner to database and linking to user: {user_id}")
        logger.debug(f"Summoner data received keys: {summoner_data.keys()}")
        
        if not self.db:
            logger.error("Database client not available")
            return None
        
        puuid = summoner_data.get('puuid')
        if not puuid:
            logger.error("No PUUID in summoner_data")
            return None
        
        # Save summoner data to database
        await self._save_summoner_to_db(summoner_data)
        
        # Create user-summoner link
        await self._create_user_summoner_link(user_id, puuid)
        
        # Ensure top_champions is in response (computed from champion_masteries)
        if 'champion_masteries' in summoner_data and summoner_data['champion_masteries']:
            # Always compute top_champions for the response
            summoner_data['top_champions'] = summoner_data['champion_masteries'][:10]
            logger.info(f"Added top_champions to response ({len(summoner_data['top_champions'])} champions)")
        else:
            logger.warning("No champion_masteries found in summoner_data")
        
        logger.debug(f"Champion masteries in summoner_data: {len(summoner_data.get('champion_masteries', []))}")
        logger.debug(f"Top champions in summoner_data: {len(summoner_data.get('top_champions', []))}")
        
        logger.info(f"Successfully saved summoner {puuid} and linked to user {user_id}")
        return SummonerResponse(**summoner_data)
    
    async def _save_summoner_to_db(self, summoner_data: dict) -> None:
        """Save summoner data to database"""
        summoner_record = SummonerRecord.from_summoner_data(summoner_data)
        logger.debug(f"Summoner record to save: {summoner_record.puuid}")
        logger.info(f"Ranked data - Solo: {summoner_record.ranked_solo_tier} {summoner_record.ranked_solo_rank}, Flex: {summoner_record.ranked_flex_tier}")
        
        self.db.table(DatabaseTable.SUMMONERS).upsert(summoner_record.to_db_dict()).execute()
        logger.info(f"Successfully upserted summoner data for PUUID: {summoner_record.puuid}")
    
    async def _create_user_summoner_link(self, user_id: str, puuid: str) -> None:
        """Create or update user-summoner link"""
        # Check if user already has ANY summoner linked
        existing_links = self.db.table(DatabaseTable.USER_SUMMONERS).select('id, puuid').eq('user_id', user_id).execute()
        
        if existing_links.data and len(existing_links.data) > 0:
            existing_link = existing_links.data[0]
            existing_puuid = existing_link.get('puuid')
            
            if existing_puuid == puuid:
                logger.debug(f"User {user_id} already linked to summoner {puuid}")
            else:
                # Update existing link to new summoner
                logger.info(f"Updating user {user_id} summoner link from {existing_puuid} to {puuid}")
                self.db.table(DatabaseTable.USER_SUMMONERS).update({'puuid': puuid}).eq('user_id', user_id).execute()
                logger.info(f"Updated user-summoner link for user {user_id}")
        else:
            # Create new link
            link_record = {'user_id': user_id, 'puuid': puuid}
            self.db.table(DatabaseTable.USER_SUMMONERS).insert(link_record).execute()
            logger.info(f"Created new user-summoner link for user {user_id}")
    
    async def get_user_summoner_from_db(self, puuid: str) -> Optional[dict]:
        """Get summoner data from database by PUUID"""
        if not self.db:
            return None
        
        response = self.db.table(DatabaseTable.SUMMONERS).select('*').eq('puuid', puuid).limit(1).execute()
        
        if response.data and len(response.data) > 0:
            return response.data[0]
        return None
    
    async def get_user_summoner(self, user_id: str) -> Optional[SummonerResponse]:
        """Get user's linked summoner from database"""
        logger.info(f"Fetching summoner for user: {user_id}")
        
        if not self.db:
            logger.error("Database client not available")
            return None
        
        response = self.db.table(DatabaseTable.USER_SUMMONERS).select(
            'puuid, summoners(*)'
        ).eq('user_id', user_id).limit(1).execute()
        
        if response.data and len(response.data) > 0:
            link = response.data[0]
            summoner = link.get('summoners')
            if summoner:
                logger.info(f"Found summoner: {summoner.get('summoner_name', 'N/A')}")
                # Use stored summoner_id if available, otherwise fallback to puuid
                summoner['id'] = summoner.get('summoner_id') or summoner.get('puuid')
                return SummonerResponse(**summoner)
        
        logger.info(f"No summoner found for user")
        return None
    
    async def get_champion_masteries(self, puuid: str, region: str = 'americas') -> List[ChampionMasteryResponse]:
        """Get all champion masteries for a summoner"""
        masteries = await self.riot_api.get_champion_masteries(puuid, region)
        return [ChampionMasteryResponse(**m) for m in masteries] if masteries else []
    
    async def get_top_champion_masteries(self, puuid: str, region: str = 'americas', count: int = 10) -> List[ChampionMasteryResponse]:
        """Get top N champion masteries for a summoner"""
        masteries = await self.riot_api.get_top_champion_masteries(puuid, region, count)
        return [ChampionMasteryResponse(**m) for m in masteries] if masteries else []
    
    async def get_mastery_score(self, puuid: str, region: str = 'americas') -> Optional[int]:
        """Get total mastery score for a summoner"""
        return await self.riot_api.get_mastery_score(puuid, region)
    
    async def get_champion_mastery_by_champion(self, puuid: str, champion_id: int, region: str = 'americas') -> Optional[ChampionMasteryResponse]:
        """Get mastery data for a specific champion"""
        mastery = await self.riot_api.get_champion_mastery_by_champion(puuid, champion_id, region)
        return ChampionMasteryResponse(**mastery) if mastery else None
    
    async def get_match_history(self, puuid: str, count: int) -> MatchHistoryResponse:
        """Get match history for a player"""
        return MatchHistoryResponse(
            puuid=puuid,
            match_ids=[f"NA1_demo_match_{i}" for i in range(count)],
            count=count
        )
    
    async def get_player_stats(self, summoner_id: str) -> Optional[PlayerStatsResponse]:
        """Get player statistics"""
        return PlayerStatsResponse(
            summoner_id=summoner_id,
            total_games=100,
            wins=55,
            losses=45,
            win_rate=55.0,
            favorite_champions=["Lux", "Ahri", "Jinx"],
            average_kda=3.2,
            average_cs_per_min=6.5
        )
