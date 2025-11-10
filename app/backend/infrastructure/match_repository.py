"""
Match repository implementation with Riot API
"""
from repositories.match_repository import MatchRepository
from repositories.riot_api_repository import RiotAPIRepository
from models.matches import MatchTimelineResponse, MatchSummaryResponse
from infrastructure.database.database_client import DatabaseClient
from constants.database import DatabaseTable
from typing import Optional, Dict, Any, List
from utils.logger import logger
from infrastructure.league_of_legends_hackathon import generate_match_analysis


class MatchRepositoryRiot(MatchRepository):
    """Riot API + Database implementation of match repository"""
    
    def __init__(self, client: DatabaseClient, riot_api_key: str):
        self.client = client
        self.riot_api_key = riot_api_key
        logger.info("Match repository initialized")
    
    async def get_match_timeline(self, match_id: str, region: str) -> Optional[MatchTimelineResponse]:
        """Get match timeline from Riot API (DEMO)"""
        # Demo implementation - would call Riot API
        return MatchTimelineResponse(
            match_id=match_id,
            frames=[],  # Would contain actual frame data
            frame_interval=60000
        )
    
    async def get_match_summary(self, match_id: str, region: str) -> Optional[MatchSummaryResponse]:
        """Get match summary from Riot API (DEMO)"""
        # Demo implementation
        return MatchSummaryResponse(
            match_id=match_id,
            game_duration=1800,
            game_mode="CLASSIC",
            game_type="MATCHED_GAME",
            participants=[],
            teams=[]
        )
    
    async def save_match_timeline(self, match_id: str, timeline_data: dict) -> Optional[MatchTimelineResponse]:
        """Save match timeline to database"""
        if self.client:
            timeline_data['match_id'] = match_id
            await self.client.table('match_timelines').upsert(timeline_data).execute()
            return MatchTimelineResponse(**timeline_data)
        return None
    
    async def get_cached_timeline(self, match_id: str) -> Optional[MatchTimelineResponse]:
        """Get cached match timeline from database"""
        if self.client:
            response = await self.client.table('match_timelines').select('*').eq('match_id', match_id).limit(1).execute()
            if response.data:
                return MatchTimelineResponse(**response.data[0])
        return None
    
    async def get_participant_data(self, match_id: str, participant_id: int) -> Optional[Dict[str, Any]]:
        """Get specific participant data from match (DEMO)"""
        # Demo implementation
        return {
            "participant_id": participant_id,
            "champion_name": "DemoChampion",
            "kills": 5,
            "deaths": 3,
            "assists": 10
        }

    # TODO: Implement match calculations either in this file or in another file

    async def save_match(
        self, 
        match_id: str, 
        match_data: Dict[str, Any], 
        puuid: str = None, 
        timeline_data: Dict[str, Any] = None,
        mastery_level: Optional[int] = None,
        mastery_points: Optional[int] = None
    ) -> bool:
        """
        Save complete match data to database and optionally track which summoner played in it
        
        Args:
            match_id: Match ID
            match_data: Full match data
            puuid: Optional PUUID of summoner to track
            timeline_data: Optional timeline data
            mastery_level: Optional mastery level (should be fetched by service layer)
            mastery_points: Optional mastery points (should be fetched by service layer)
            
        Note:
            Mastery data is optional. If not provided, champion progress will be updated
            without mastery info. Mastery can be updated later via explicit champion progress updates.
        """
        try:
            if not self.client:
                logger.error("Database client not available")
                return False
            
            # Check if match exists and get current summoners list + timeline
            existing = await self.client.table(DatabaseTable.MATCHES).select('summoners, timeline_data').eq('match_id', match_id).limit(1).execute()
            
            summoners = []
            existing_timeline = None
            is_new_match = False
            if existing.data and len(existing.data) > 0:
                # Match exists, get current summoners list and timeline
                summoners = existing.data[0].get('summoners', [])
                existing_timeline = existing.data[0].get('timeline_data')
            else:
                is_new_match = True
            
            # Add this summoner if provided and not already in list
            if puuid and puuid not in summoners:
                summoners.append(puuid)
                logger.debug(f"Adding summoner {puuid} to match {match_id}")
            
            # Preserve existing timeline if not provided (don't overwrite with None!)
            final_timeline = timeline_data if timeline_data is not None else existing_timeline
            
            # Build analysis JSON when both match and timeline data are present
            analysis = None
            try:
                if match_data and final_timeline:
                    analysis = generate_match_analysis(match_id, match_data, final_timeline)
                    logger.debug(f"Generated analysis for match {match_id}")
            except Exception as gen_err:
                logger.error(f"Failed to generate analysis for match {match_id}: {gen_err}")
            
            # Extract metadata from match_data
            info = match_data.get('info', {})
            metadata = match_data.get('metadata', {})
            
            match_record = {
                'match_id': match_id,
                'game_creation': info.get('gameCreation', 0),
                'game_duration': info.get('gameDuration', 0),
                'game_end_timestamp': info.get('gameEndTimestamp'),
                'game_mode': info.get('gameMode', ''),
                'game_type': info.get('gameType', ''),
                'game_version': info.get('gameVersion', ''),
                'map_id': info.get('mapId', 0),
                'platform_id': info.get('platformId', ''),
                'queue_id': info.get('queueId', 0),
                'match_data': match_data,
                'timeline_data': final_timeline,  # Use preserved timeline
                'summoners': summoners,
                'analysis': analysis  # Computed analysis with Chart.js visualizations
            }
            
            await self.client.table(DatabaseTable.MATCHES).upsert(match_record).execute()
            
            # Update champion progress for tracked summoners (only for new matches with analysis)
            if is_new_match and analysis and puuid:
                await self._update_champion_progress_for_match(
                    match_id, match_data, analysis, puuid, mastery_level, mastery_points
                )
            
            timeline_status = "with timeline" if final_timeline else "without timeline"
            if existing_timeline and not timeline_data:
                logger.info(f"Updated match: {match_id} (preserved existing timeline, tracked summoners: {len(summoners)})")
            else:
                logger.info(f"Saved match: {match_id} ({timeline_status}, tracked summoners: {len(summoners)})")
            return True
            
        except Exception as e:
            logger.error(f"Error saving match {match_id}: {e}")
            return False
    
    async def get_match(self, match_id: str) -> Optional[Dict[str, Any]]:
        """Get complete match data from database"""
        try:
            if not self.client:
                logger.error("Database client not available")
                return None
            
            result = await self.client.table(str(DatabaseTable.MATCHES))\
                .select('match_data')\
                .eq('match_id', match_id)\
                .limit(1)\
                .execute()
            
            if result.data and len(result.data) > 0:
                logger.info(f"Retrieved match from database: {match_id}")
                return result.data[0].get('match_data')
            
            logger.info(f"Match not found in database: {match_id}")
            return None
            
        except Exception as e:
            logger.error(f"Error retrieving match {match_id}: {e}")
            return None
    
    async def get_match_with_timeline(self, match_id: str) -> Optional[Dict[str, Any]]:
        """Get complete match data with timeline and analysis from database"""
        try:
            if not self.client:
                logger.error("Database client not available")
                return None
            
            result = await self.client.table(str(DatabaseTable.MATCHES))\
                .select('match_data, timeline_data, analysis')\
                .eq('match_id', match_id)\
                .limit(1)\
                .execute()
            
            if result.data and len(result.data) > 0:
                logger.debug(f"Retrieved match with timeline and analysis from database: {match_id}")
                record = result.data[0]
                # Log the actual data values
                timeline_val = record.get('timeline_data')
                analysis_val = record.get('analysis')
                logger.info(f"Raw timeline_data type: {type(timeline_val)}, is None: {timeline_val is None}, value preview: {str(timeline_val)[:100] if timeline_val else 'None'}")
                logger.info(f"Raw analysis type: {type(analysis_val)}, is None: {analysis_val is None}")
                return record
            
            logger.info(f"Match not found in database: {match_id}")
            return None
            
        except Exception as e:
            logger.error(f"Error retrieving match with timeline and analysis {match_id}: {e}")
            return None
    
    async def get_matches_for_puuid(self, puuid: str, start_index: int = 0, count: int = 10) -> List[Any]:
        """
        Get matches for a specific PUUID with pagination by querying matches table directly.
        Returns matches ordered by game_creation descending (newest first).
        """
        try:
            if not self.client:
                logger.error("Database client not available")
                return []
            
            # Query matches where the PUUID exists in participants
            # Use JSONB containment operator to find matches
            # Note: Supabase uses .limit() for pagination, we'll fetch more and slice in Python
            result = await self.client.table(str(DatabaseTable.MATCHES))\
                .select('match_id, match_data, timeline_data, analysis, game_creation')\
                .contains('match_data', {'info': {'participants': [{'puuid': puuid}]}})\
                .order('game_creation', desc=True)\
                .limit(start_index + count)\
                .execute()
            
            # Slice the results to get the correct page
            if result.data:
                result.data = result.data[start_index:start_index + count]
            
            if not result.data:
                logger.info(f"No matches found for PUUID: {puuid} at index {start_index}")
                return []
            
            logger.info(f"Found {len(result.data)} matches for PUUID: {puuid} (indices {start_index}-{start_index + len(result.data) - 1})")
            
            # Convert to FullGameData format
            from models.match import FullGameData
            full_games = []
            for match in result.data:
                full_game = FullGameData(
                    match_id=match['match_id'],
                    match_data=match.get('match_data', {}),
                    timeline_data=match.get('timeline_data'),
                    analysis=match.get('analysis')
                )
                full_games.append(full_game)
            
            return full_games
            
        except Exception as e:
            logger.error(f"Error retrieving matches for PUUID {puuid}: {e}")
            return []
    
    async def match_exists(self, match_id: str) -> bool:
        """Check if match exists in database"""
        if not self.client:
            return False
        
        try:
            result = await self.client.table(DatabaseTable.MATCHES) \
                .select('match_id') \
                .eq('match_id', match_id) \
                .limit(1) \
                .execute()
            
            exists = result.data and len(result.data) > 0
            logger.debug(f"Match {match_id} exists: {exists}")
            return exists
            
        except Exception as e:
            logger.error(f"Error checking match existence: {e}")
            return False
    
    async def match_exists_for_summoner(self, match_id: str, puuid: str) -> bool:
        """
        Check if match exists AND if this summoner is already tracked in it
        
        Args:
            match_id: Match ID
            puuid: Summoner PUUID
            
        Returns:
            True if match exists and summoner is tracked, False otherwise
        """
        if not self.client:
            return False
        
        try:
            result = await self.client.table(DatabaseTable.MATCHES) \
                .select('summoners') \
                .eq('match_id', match_id) \
                .limit(1) \
                .execute()
            
            if result.data and len(result.data) > 0:
                summoners = result.data[0].get('summoners', [])
                exists_for_summoner = puuid in summoners
                logger.debug(f"Match {match_id} exists for summoner {puuid}: {exists_for_summoner}")
                return exists_for_summoner
            
            return False
            
        except Exception as e:
            logger.error(f"Error checking match for summoner: {e}")
            return False
    
    async def get_player_matches(self, puuid: str, limit: int = 20) -> List[Dict[str, Any]]:
        """Get all matches for a specific player using JSONB query"""
        try:
            if not self.client:
                logger.error("Database client not available")
                return []
            
            # Query matches where the player's PUUID is in the participants array
            # This uses PostgreSQL's JSONB containment operator
            result = await self.client.table(str(DatabaseTable.MATCHES))\
                .select('*')\
                .contains('match_data->metadata->participants', [puuid])\
                .order('game_creation', desc=True)\
                .limit(limit)\
                .execute()
            
            if result.data:
                logger.info(f"Retrieved {len(result.data)} matches for player {puuid}")
                return result.data
            
            logger.info(f"No matches found for player {puuid}")
            return []
            
        except Exception as e:
            logger.error(f"Error retrieving matches for player {puuid}: {e}")
            return []
    
    async def sync_player_matches(self, puuid: str, region: str, riot_api: RiotAPIRepository, max_matches: int = 100) -> int:
        """
        Sync matches for a player from Riot API to database.
        Fetches matches in batches and stops when hitting existing ones or reaching max_matches.
        
        Args:
            puuid: Player's PUUID
            region: Regional routing value
            riot_api: RiotAPIRepository instance
            max_matches: Maximum number of matches to sync (default 100)
        """
        try:
            total_saved = 0
            start_index = 0
            batch_size = min(100, max_matches)  # Riot API max is 100
            
            # Quick check: if first match exists, nothing to sync
            if await self.is_match_history_synced(puuid, region, riot_api):
                logger.info(f"Match history already up to date for {puuid}")
                return 0
            
            while True:
                # Check if we've reached the max
                if total_saved >= max_matches:
                    logger.info(f"Reached max matches limit ({max_matches}) - stopping sync")
                    break
                
                # Adjust batch size if we're near the limit
                remaining = max_matches - total_saved
                current_batch_size = min(batch_size, remaining)
                
                # Fetch batch of match IDs
                logger.info(f"Fetching match IDs batch starting at index {start_index} (max {current_batch_size})")
                match_ids = await riot_api.get_match_ids_by_puuid(puuid, region, count=current_batch_size, start=start_index)
                
                if not match_ids or len(match_ids) == 0:
                    logger.info(f"No more matches found - sync complete ({total_saved} total saved)")
                    break
                
                logger.info(f"Found {len(match_ids)} match IDs in this batch")
                
                # Process batch
                batch_saved = 0
                should_stop = False
                
                for i, match_id in enumerate(match_ids):
                    # Check if match already exists
                    exists = await self.match_exists(match_id)
                    
                    if exists:
                        logger.info(f"Match {match_id} already exists - stopping sync ({total_saved} total saved)")
                        should_stop = True
                        break
                    
                    # Fetch and save match
                    logger.info(f"Fetching match details for: {match_id} (#{start_index + i + 1})")
                    match_data = await riot_api.get_match_details(match_id, region)
                    
                    if not match_data:
                        logger.warning(f"Could not fetch match details for: {match_id}")
                        continue
                    
                    # Save to database
                    if await self.save_match(match_id, match_data):
                        batch_saved += 1
                        total_saved += 1
                        logger.info(f"Saved match {match_id} ({total_saved} total saved)")
                    else:
                        logger.error(f"Failed to save match: {match_id}")
                
                # If we hit an existing match, stop
                if should_stop:
                    break
                
                # If we got fewer matches than requested, we've reached the end
                if len(match_ids) < batch_size:
                    logger.info(f"Reached end of match history ({total_saved} total saved)")
                    break
                
                # Move to next batch
                start_index += batch_size
            
            logger.info(f"Match sync complete: {total_saved} new matches saved")
            return total_saved
            
        except Exception as e:
            logger.error(f"Error syncing match history for {puuid}: {e}")
            return 0
    
    async def _update_champion_progress_for_match(
        self, 
        match_id: str, 
        match_data: Dict[str, Any], 
        analysis: Dict[str, Any], 
        puuid: str,
        mastery_level: Optional[int] = None,
        mastery_points: Optional[int] = None
    ) -> None:
        """
        Update champion progress after processing a match.
        This is called internally when a new match is saved with analysis.
        Mastery data should be provided by the caller (service layer).
        """
        try:
            from infrastructure.champion_progress_repository import ChampionProgressRepositorySupabase
            from models.champion_progress import UpdateChampionProgressRequest
            
            # Find the participant for this PUUID
            participants = match_data.get('info', {}).get('participants', [])
            participant = next((p for p in participants if p.get('puuid') == puuid), None)
            
            if not participant:
                logger.warning(f"Could not find participant with PUUID {puuid} in match {match_id}")
                return
            
            # Extract champion info
            champion_id = participant.get('championId')
            champion_name = participant.get('championName')
            
            if not champion_id or not champion_name:
                logger.warning(f"Missing champion info for PUUID {puuid} in match {match_id}")
                return
            
            # Get EPS score from analysis
            eps_scores = analysis.get('rawStats', {}).get('epsScores', {})
            eps_score = eps_scores.get(champion_name, 0.0)
            
            # Get final CPS from power score timeline and normalize by game length
            cps_score = 0.0
            power_timeline = analysis.get('charts', {}).get('powerScoreTimeline', {})
            game_duration_minutes = match_data.get('info', {}).get('gameDuration', 0) / 60  # Convert seconds to minutes
            
            if power_timeline and game_duration_minutes > 0:
                datasets = power_timeline.get('data', {}).get('datasets', [])
                for dataset in datasets:
                    label = dataset.get('label', '')
                    if champion_name in label:
                        data_points = dataset.get('data', [])
                        if data_points:
                            final_cps = data_points[-1]  # Final cumulative power score
                            cps_score = final_cps / game_duration_minutes  # Normalize by game length
                        break
            
            # Calculate KDA
            kills = participant.get('kills', 0)
            deaths = participant.get('deaths', 0)
            assists = participant.get('assists', 0)
            kda = round((kills + assists) / max(deaths, 1), 2)
            
            # Get user_id from user_summoners table
            user_result = await self.client.table(DatabaseTable.USER_SUMMONERS).select('user_id').eq('puuid', puuid).limit(1).execute()
            
            if not user_result.data or len(user_result.data) == 0:
                logger.debug(f"No user_id found for PUUID {puuid} - skipping champion progress update")
                return
            
            user_id = user_result.data[0].get('user_id')
            
            # Create update request
            update_request = UpdateChampionProgressRequest(
                match_id=match_id,
                champion_id=champion_id,
                champion_name=champion_name,
                eps_score=eps_score,
                cps_score=cps_score,
                kda=kda,
                win=participant.get('win', False),
                kills=kills,
                deaths=deaths,
                assists=assists,
                cs=participant.get('totalMinionsKilled', 0) + participant.get('neutralMinionsKilled', 0),
                gold=participant.get('goldEarned', 0),
                damage=participant.get('totalDamageDealtToChampions', 0),
                vision_score=participant.get('visionScore', 0),
                game_date=match_data.get('info', {}).get('gameCreation', 0) // 1000  # Convert to seconds
            )
            
            # Fetch current mastery data if not provided (mastery changes after each game)
            if mastery_level is None or mastery_points is None:
                try:
                    # Get region
                    region_result = await self.client.table(DatabaseTable.SUMMONERS).select('region').eq('puuid', puuid).limit(1).execute()
                    region = region_result.data[0].get('region', 'americas') if region_result.data else 'americas'
                    
                    # Import here to avoid circular dependency
                    from infrastructure.player_repository import PlayerRepositoryRiot
                    from infrastructure.riot_api_repository import RiotAPIRepositoryImpl
                    from config.riot_api import riot_api_config
                    
                    riot_api = RiotAPIRepositoryImpl(riot_api_config)
                    player_repo = PlayerRepositoryRiot(self.client, riot_api)
                    mastery_data = await player_repo.get_champion_mastery_by_champion(puuid, champion_id, region)
                    
                    if mastery_data:
                        mastery_level = mastery_data.champion_level
                        mastery_points = mastery_data.champion_points
                        logger.debug(f"Fetched current mastery for {champion_name}: Level {mastery_level}, {mastery_points} points")
                except Exception as e:
                    logger.warning(f"Could not fetch mastery for {champion_name}: {e}")
            
            # Update champion progress with mastery data
            progress_repo = ChampionProgressRepositorySupabase(self.client)
            result = await progress_repo.update_champion_progress(user_id, puuid, update_request, mastery_level, mastery_points)
            
            if result:
                logger.info(f"✅ Updated champion progress for {champion_name} (user: {user_id}, match: {match_id})")
            else:
                logger.warning(f"Failed to update champion progress for {champion_name} (match: {match_id})")
                
        except Exception as e:
            logger.error(f"Error updating champion progress for match {match_id}: {e}")
            # Don't raise - this is a non-critical operation
    
    async def is_match_history_synced(self, puuid: str, region: str, riot_api: RiotAPIRepository) -> bool:
        """Check if player's match history is already synced by checking first match"""
        try:
            # Get just the first match ID
            match_ids = await riot_api.get_match_ids_by_puuid(puuid, region, count=1, start=0)
            
            if not match_ids:
                return True  # No matches to sync
            
            # Check if first match exists
            exists = await self.match_exists(match_ids[0])
            
            if exists:
                logger.debug(f"First match {match_ids[0]} exists - already synced")
            
            return exists
            
        except Exception as e:
            logger.error(f"Error checking sync status: {e}")
            return False
