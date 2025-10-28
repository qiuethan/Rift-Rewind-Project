"""
Player repository implementation with Riot API
"""
from repositories.player_repository import PlayerRepository
from repositories.riot_api_repository import RiotAPIRepository
from models.players import SummonerResponse, PlayerStatsResponse, SummonerRecord
from models.riot_api import RankedData, MasteryData, ChampionMasteryResponse, MatchHistoryResponse
from models.match import RecentGameSummary
from infrastructure.database.database_client import DatabaseClient
from constants.database import DatabaseTable
from typing import Optional, List, Dict, Any
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
    
    async def get_account_by_riot_id(self, game_name: str, tag_line: str, region: str) -> Optional[Dict[str, Any]]:
        """Get account data (PUUID) by Riot ID - simple data access"""
        logger.info(f"Fetching account: {game_name}#{tag_line} in {region}")
        
        try:
            account_data = await self.riot_api.get_account_by_riot_id(game_name, tag_line, region)
            if not account_data:
                logger.warning(f"Account not found: {game_name}#{tag_line}")
                return None
            
            logger.info(f"Successfully fetched account for {game_name}#{tag_line}")
            return account_data
            
        except Exception as e:
            logger.error(f"Error fetching account: {str(e)}")
            return None
    
    async def get_summoner_by_riot_id(self, game_name: str, tag_line: str, region: str) -> Optional[SummonerResponse]:
        """
        Get summoner by Riot ID - orchestration moved to service layer
        This is a convenience method that combines get_account + get_summoner_by_puuid
        """
        logger.info(f"Fetching summoner by Riot ID: {game_name}#{tag_line} in {region}")
        
        try:
            # Get account (PUUID)
            account_data = await self.get_account_by_riot_id(game_name, tag_line, region)
            if not account_data or not account_data.get('puuid'):
                return None
            
            puuid = account_data['puuid']
            
            # Get summoner data
            summoner_data = await self.get_summoner_by_puuid(puuid, region)
            if not summoner_data:
                return None
            
            # Build response
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
            
            logger.info(f"Successfully fetched summoner: {response.summoner_name} (Level {response.summoner_level})")
            return response
            
        except Exception as e:
            logger.error(f"Error fetching summoner from Riot API: {str(e)}")
            return None
    
    async def get_summoner_by_puuid(self, puuid: str, region: str = 'americas') -> Optional[Dict[str, Any]]:
        """
        Get basic summoner data by PUUID from Riot API
        Returns raw summoner data - orchestration should be done in service layer
        """
        logger.info(f"Fetching summoner by PUUID: {puuid}")
        
        try:
            summoner_data = await self.riot_api.get_summoner_by_puuid(puuid, region)
            if not summoner_data:
                logger.warning(f"Summoner not found for PUUID: {puuid}")
                return None
            
            logger.info(f"Successfully fetched summoner data for PUUID: {puuid}")
            return summoner_data
            
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
            logger.info("Ranked data fetched (not used)")
            
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
            logger.info("Ranked data fetched (not used)")
            
            return ranked_data
                
        except Exception as e:
            logger.error(f"Error fetching ranked data: {str(e)}")
            return RankedData()
    
    async def get_cached_recent_games(self, puuid: str, count: int) -> Optional[List[RecentGameSummary]]:
        """Get cached recent games from summoners table"""
        if not self.db:
            return None
        
        try:
            result = await self.db.table(DatabaseTable.SUMMONERS).select('recent_games').eq('puuid', puuid).limit(1).execute()
            
            if result.data and len(result.data) > 0:
                cached_games = result.data[0].get('recent_games', [])
                if cached_games:
                    # Convert dicts to RecentGameSummary models
                    return [RecentGameSummary(**game) for game in cached_games[:count]]
            
            return None
        except Exception as e:
            logger.error(f"Error getting cached games: {e}")
            return None
    
    async def get_match_from_db(self, match_id: str) -> Optional[Dict[str, Any]]:
        """Get match data from matches table"""
        if not self.db:
            return None
        
        try:
            result = await self.db.table(DatabaseTable.MATCHES).select('match_data').eq('match_id', match_id).limit(1).execute()
            
            if result.data and len(result.data) > 0:
                return result.data[0].get('match_data')
            
            return None
        except Exception as e:
            logger.error(f"Error getting match from DB: {e}")
            return None
    
    async def get_matches_from_db(self, match_ids: List[str], puuid: str) -> List[RecentGameSummary]:
        """Get multiple matches from database and extract game summaries"""
        games = []
        
        for match_id in match_ids:
            match_data = await self.get_match_from_db(match_id)
            
            if match_data:
                game_summary = self._extract_game_summary(match_data, puuid, match_id)
                if game_summary:
                    games.append(game_summary)
            else:
                logger.warning(f"Match {match_id} not in DB")
        
        return games
    
    async def fetch_and_build_games(self, match_ids: List[str], puuid: str, region: str) -> List[RecentGameSummary]:
        """Fetch match details (checking DB first) and build game summaries - CONCURRENT"""
        logger.info(f"🔄 fetch_and_build_games called with {len(match_ids)} match IDs for PUUID: {puuid}")
        
        async def process_match(match_id: str) -> Optional[RecentGameSummary]:
            """Process a single match"""
            try:
                # Try DB first
                match_data = await self.get_match_from_db(match_id)
                
                if not match_data:
                    # Not in DB, fetch from API
                    logger.info(f"⬇️ Match {match_id} NOT in DB - fetching from API")
                    match_data = await self.riot_api.get_match_details(match_id, region)
                    
                    # If fetched from API, also save it to DB with timeline
                    if match_data:
                        try:
                            # Fetch timeline data concurrently with match data
                            timeline_data = await self.riot_api.get_match_timeline(match_id, region)
                            logger.info(f"✅ Match + Timeline fetched for {match_id}")
                            
                            # Save to DB with this summoner tracked
                            from infrastructure.match_repository import MatchRepositoryRiot
                            api_key = self.riot_api.riot.api_key if hasattr(self.riot_api, 'riot') else None
                            match_repo = MatchRepositoryRiot(self.db, api_key)
                            await match_repo.save_match(match_id, match_data, puuid, timeline_data)
                            logger.info(f"✅ Saved match {match_id} to DB")
                        except Exception as e:
                            logger.error(f"❌ Error saving match {match_id}: {e}")
                    else:
                        logger.warning(f"⚠️ No match data returned from API for {match_id}")
                else:
                    # Match exists in DB - ensure this summoner is tracked
                    logger.debug(f"Using cached match: {match_id}")
                    try:
                        from infrastructure.match_repository import MatchRepositoryRiot
                        api_key = self.riot_api.riot.api_key if hasattr(self.riot_api, 'riot') else None
                        match_repo = MatchRepositoryRiot(self.db, api_key)
                        await match_repo.save_match(match_id, match_data, puuid)
                    except Exception as e:
                        logger.error(f"Error updating match {match_id} summoners: {e}")
                
                if match_data:
                    return self._extract_game_summary(match_data, puuid, match_id)
                return None
            except Exception as e:
                logger.error(f"❌ Error processing match {match_id}: {e}")
                return None
        
        # Process all matches concurrently
        logger.info(f"🚀 Processing {len(match_ids)} matches CONCURRENTLY")
        tasks = [process_match(match_id) for match_id in match_ids]
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Filter out None and exceptions
        games = [game for game in results if game is not None and not isinstance(game, Exception)]
        logger.info(f"✅ Completed: {len(games)}/{len(match_ids)} matches processed successfully")
        
        return games
    
    async def update_recent_games_cache(self, puuid: str, games: List[RecentGameSummary]) -> None:
        """Update the recent_games cache in summoners table"""
        if not self.db or not games:
            logger.warning(f"Cannot update cache: db={self.db is not None}, games={len(games) if games else 0}")
            return
        
        try:
            # Convert models to dicts for database storage
            games_dicts = [game.dict() for game in games]
            
            logger.info(f"Updating recent_games cache for {puuid} with {len(games_dicts)} games")
            
            await self.db.table(DatabaseTable.SUMMONERS).update(
                {'recent_games': games_dicts}
            ).eq('puuid', puuid).execute()
            
            logger.info(f"✅ Successfully updated recent_games cache with {len(games)} games")
        except Exception as e:
            logger.error(f"❌ Error updating cache: {e}")
    
    def _extract_game_summary(self, match_data: dict, puuid: str, match_id: str) -> Optional[RecentGameSummary]:
        """Extract game summary for a specific player from match data"""
        try:
            # Find the participant data for this player
            participant = None
            for p in match_data.get('info', {}).get('participants', []):
                if p.get('puuid') == puuid:
                    participant = p
                    break
            
            if not participant:
                logger.warning(f"Could not find participant data in match {match_id}")
                return None
            
            # Create RecentGameSummary model
            game_summary = RecentGameSummary(
                match_id=match_id,
                game_mode=match_data.get('info', {}).get('gameMode', 'UNKNOWN'),
                game_duration=match_data.get('info', {}).get('gameDuration', 0),
                game_creation=match_data.get('info', {}).get('gameCreation', 0),
                champion_id=participant.get('championId'),
                champion_name=participant.get('championName'),
                kills=participant.get('kills', 0),
                deaths=participant.get('deaths', 0),
                assists=participant.get('assists', 0),
                win=participant.get('win', False),
                cs=participant.get('totalMinionsKilled', 0) + participant.get('neutralMinionsKilled', 0),
                gold=participant.get('goldEarned', 0),
                damage=participant.get('totalDamageDealtToChampions', 0),
                vision_score=participant.get('visionScore', 0),
                items=[
                    participant.get('item0', 0),
                    participant.get('item1', 0),
                    participant.get('item2', 0),
                    participant.get('item3', 0),
                    participant.get('item4', 0),
                    participant.get('item5', 0),
                    participant.get('item6', 0),  # Trinket
                    participant.get('item7', 0),  # Jungle pet (Season 14+)
                ]
            )
            
            logger.debug(f"Processed match {match_id}: {game_summary.champion_name} - {'Win' if game_summary.win else 'Loss'}")
            return game_summary
            
        except Exception as e:
            logger.error(f"Error extracting game summary from match {match_id}: {e}")
            return None
    
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
        logger.info(f"Saving summoner: {summoner_record.summoner_name}, Level: {summoner_record.summoner_level}")
        
        await self.db.table(DatabaseTable.SUMMONERS).upsert(summoner_record.to_db_dict()).execute()
        logger.info(f"Successfully upserted summoner data for PUUID: {summoner_record.puuid}")
    
    async def _create_user_summoner_link(self, user_id: str, puuid: str) -> None:
        """Create or update user-summoner link"""
        # Check if user already has ANY summoner linked
        existing_links = await self.db.table(DatabaseTable.USER_SUMMONERS).select('id, puuid').eq('user_id', user_id).execute()
        
        if existing_links.data and len(existing_links.data) > 0:
            existing_link = existing_links.data[0]
            existing_puuid = existing_link.get('puuid')
            
            if existing_puuid == puuid:
                logger.debug(f"User {user_id} already linked to summoner {puuid}")
            else:
                # Update existing link to new summoner
                logger.info(f"Updating user {user_id} summoner link from {existing_puuid} to {puuid}")
                await self.db.table(DatabaseTable.USER_SUMMONERS).update({'puuid': puuid}).eq('user_id', user_id).execute()
                logger.info(f"Updated user-summoner link for user {user_id}")
        else:
            # Create new link
            link_record = {'user_id': user_id, 'puuid': puuid}
            await self.db.table(DatabaseTable.USER_SUMMONERS).insert(link_record).execute()
            logger.info(f"Created new user-summoner link for user {user_id}")
    
    async def get_user_summoner_from_db(self, puuid: str) -> Optional[dict]:
        """Get summoner data from database by PUUID"""
        if not self.db:
            return None
        
        response = await self.db.table(DatabaseTable.SUMMONERS).select('*').eq('puuid', puuid).limit(1).execute()
        
        if response.data and len(response.data) > 0:
            return response.data[0]
        return None
    
    async def get_user_summoner_basic(self, user_id: str) -> Optional[dict]:
        """Get basic user summoner info (PUUID and region) without fetching fresh data"""
        if not self.db:
            return None
        
        response = await self.db.table(DatabaseTable.USER_SUMMONERS).select(
            'puuid, summoners(region)'
        ).eq('user_id', user_id).limit(1).execute()
        
        if not response.data or len(response.data) == 0:
            return None
        
        puuid = response.data[0].get('puuid')
        summoner_db = response.data[0].get('summoners')
        
        if not summoner_db:
            return None
        
        return {
            'puuid': puuid,
            'region': summoner_db.get('region', 'americas')
        }
    
    async def get_user_summoner_last_update(self, user_id: str) -> Optional[datetime]:
        """Get the last update timestamp for a user's linked summoner"""
        if not self.db:
            return None
        
        try:
            response = await self.db.table(DatabaseTable.USER_SUMMONERS).select(
                'updated_at'
            ).eq('user_id', user_id).limit(1).execute()
            
            if response.data and len(response.data) > 0:
                updated_at_str = response.data[0].get('updated_at')
                if updated_at_str:
                    # Parse ISO format timestamp from Supabase
                    from datetime import datetime
                    return datetime.fromisoformat(updated_at_str.replace('Z', '+00:00'))
            
            return None
        except Exception as e:
            logger.error(f"Error getting last update time: {e}")
            return None
    
    async def get_user_summoner(self, user_id: str) -> Optional[SummonerResponse]:
        """Get user's linked summoner and fetch fresh data from Riot API"""
        logger.info(f"Fetching summoner for user: {user_id}")
        
        if not self.db:
            logger.error("Database client not available")
            return None
        
        # Get user's linked PUUID and region from database
        response = await self.db.table(DatabaseTable.USER_SUMMONERS).select(
            'puuid, summoners(region, summoner_name, game_name, tag_line)'
        ).eq('user_id', user_id).limit(1).execute()
        
        if not response.data or len(response.data) == 0:
            logger.info(f"No summoner linked for user: {user_id}")
            return None
        
        puuid = response.data[0].get('puuid')
        summoner_db = response.data[0].get('summoners')
        
        if not summoner_db:
            logger.warning(f"Summoner data not found in database for PUUID: {puuid}")
            return None
        
        region = summoner_db.get('region', 'americas')
        
        logger.info(f"Fetching fresh data from Riot API for PUUID: {puuid}")
        
        # Just return cached data from DB - service layer handles fresh data fetching
        try:
            cached_response = await self.db.table(DatabaseTable.SUMMONERS).select('*').eq('puuid', puuid).limit(1).execute()
            if cached_response.data and len(cached_response.data) > 0:
                cached_data = cached_response.data[0]
                cached_data['id'] = cached_data.get('summoner_id') or cached_data.get('puuid')
                logger.info(f"Returning cached summoner data for PUUID: {puuid}")
                return SummonerResponse(**cached_data)
            
            logger.warning(f"No cached data found for PUUID: {puuid}")
            return None
            
        except Exception as e:
            logger.error(f"Error fetching fresh summoner data: {str(e)}")
            # Fallback to cached data
            cached_response = await self.db.table(DatabaseTable.SUMMONERS).select('*').eq('puuid', puuid).limit(1).execute()
            if cached_response.data and len(cached_response.data) > 0:
                logger.info("Returning cached data due to API error")
                cached_data = cached_response.data[0]
                cached_data['id'] = cached_data.get('summoner_id') or cached_data.get('puuid')
                return SummonerResponse(**cached_data)
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
