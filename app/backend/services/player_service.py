"""
Player service - Orchestrates player operations
"""
from repositories.player_repository import PlayerRepository
from repositories.match_repository import MatchRepository
from repositories.riot_api_repository import RiotAPIRepository
from domain.player_domain import PlayerDomain
from domain.exceptions import DomainException
from models.players import SummonerRequest, SummonerResponse, PlayerStatsResponse
from models.match import RecentGameSummary
from fastapi import HTTPException, status
from typing import List
from datetime import datetime
from utils.logger import logger


class PlayerService:
    """Service for player operations - pure orchestration"""
    
    def __init__(
        self, 
        player_repository: PlayerRepository, 
        player_domain: PlayerDomain,
        match_repository: MatchRepository,
        riot_api_repository: RiotAPIRepository
    ):
        self.player_repository = player_repository
        self.player_domain = player_domain
        self.match_repository = match_repository
        self.riot_api = riot_api_repository
    
    async def link_summoner(self, user_id: str, summoner_request: SummonerRequest) -> SummonerResponse:
        """Link summoner account to user"""
        # Validate with domain - catch domain exceptions and convert to HTTP
        try:
            self.player_domain.validate_region(summoner_request.region)
        except DomainException as e:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=e.message)
        
        logger.debug(f"Received request - game_name: '{summoner_request.game_name}', tag_line: '{summoner_request.tag_line}', summoner_name: '{summoner_request.summoner_name}'")
        
        has_riot_id = summoner_request.game_name and summoner_request.tag_line and \
                      summoner_request.game_name.strip() and summoner_request.tag_line.strip()
        has_summoner_name = summoner_request.summoner_name and summoner_request.summoner_name.strip()
        
        logger.debug(f"Validation check - has_riot_id: {has_riot_id}, has_summoner_name: {has_summoner_name}")
        
        if has_riot_id:
            summoner = await self.player_repository.get_summoner_by_riot_id(
                summoner_request.game_name.strip(),
                summoner_request.tag_line.strip(),
                summoner_request.region
            )
        elif has_summoner_name:
            try:
                self.player_domain.validate_summoner_name(summoner_request.summoner_name)
            except DomainException as e:
                raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=e.message)
            summoner = await self.player_repository.get_summoner_by_name(
                summoner_request.summoner_name.strip(),
                summoner_request.region
            )
        else:
            logger.error(f"Validation failed - game_name: '{summoner_request.game_name}', tag_line: '{summoner_request.tag_line}', summoner_name: '{summoner_request.summoner_name}'")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Must provide either game_name+tag_line or summoner_name"
            )
        
        if not summoner:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Summoner not found"
            )
        
        logger.info(f"Fetching mastery data for summoner: {summoner.puuid}")
        
        mastery_data = await self.player_repository.get_mastery_data(summoner.puuid, summoner_request.region)
        logger.info(f"Mastery data fetched: {len(mastery_data.champion_masteries)} masteries")
        
        summoner_data = summoner.dict()
        logger.debug(f"Base summoner data: {summoner_data}")
        
        summoner_data.update(mastery_data.to_dict())  # Use to_dict() for proper JSONB conversion
        # recent_games will be populated after initial match sync
        summoner_data['recent_games'] = []
        logger.debug(f"After updates: champion_masteries={len(summoner_data.get('champion_masteries', []))}")
        
        # Ensure game_name and tag_line are set
        if summoner_request.game_name:
            summoner_data['game_name'] = summoner_request.game_name
        if summoner_request.tag_line:
            summoner_data['tag_line'] = summoner_request.tag_line
        
        logger.debug(f"Saving complete summoner data to database: {summoner_data.keys()}")
        result = await self.player_repository.save_summoner(user_id, summoner_data)
        
        if not result:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to save summoner"
            )
        
        # Fetch first 10 matches synchronously (for immediate display)
        logger.info(f"Fetching initial 10 matches for {summoner.puuid}")
        initial_games = await self.sync_initial_matches(summoner.puuid, summoner_request.region, count=10)
        
        # Save initial games to recent_games cache
        if initial_games:
            await self.player_repository.update_recent_games_cache(summoner.puuid, initial_games)
        
        # Schedule background task to fetch ALL remaining matches with rate limiting
        # This runs asynchronously and won't block the response
        import asyncio
        asyncio.create_task(self._sync_all_matches_with_rate_limit(summoner.puuid, summoner_request.region))
        
        return result
    
    async def get_summoner(self, user_id: str) -> SummonerResponse:
        """Get user's linked summoner with fresh data (orchestrates multiple data sources)"""
        # Get cached summoner from DB
        db_summoner = await self.player_repository.get_user_summoner(user_id)
        
        if not db_summoner:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="No summoner linked to this account"
            )
        
        logger.info(f"Fetching fresh data for summoner: {db_summoner.puuid} in region: {db_summoner.region}")
        
        try:
            # Fetch fresh summoner data from Riot API
            summoner_data = await self.player_repository.get_summoner_by_puuid(db_summoner.puuid, db_summoner.region)
            
            if not summoner_data:
                logger.warning("Could not fetch fresh summoner data")
                return db_summoner
            
            # Fetch mastery data
            mastery_data = await self.player_repository.get_mastery_data(db_summoner.puuid, db_summoner.region)
            logger.info(f"Fetched {len(mastery_data.champion_masteries)} masteries")
            
            # Build SummonerResponse with fresh data
            fresh_summoner = SummonerResponse(
                id=summoner_data.get('id', db_summoner.puuid),
                summoner_name=db_summoner.summoner_name,
                game_name=db_summoner.game_name,
                tag_line=db_summoner.tag_line,
                puuid=db_summoner.puuid,
                region=db_summoner.region,
                summoner_level=summoner_data.get('summonerLevel', db_summoner.summoner_level),
                profile_icon_id=summoner_data.get('profileIconId', db_summoner.profile_icon_id),
                last_updated=datetime.utcnow().isoformat() + "Z",
                **mastery_data.dict()
            )
            
            logger.info(f"Successfully built fresh summoner response")
            return fresh_summoner
            
        except Exception as e:
            logger.error(f"Error fetching fresh summoner data: {str(e)}", exc_info=True)
            # Fallback to DB data
            logger.warning("Returning cached data from DB")
            return db_summoner
    
    async def get_player_stats(self, summoner_id: str) -> PlayerStatsResponse:
        """Get player statistics"""
        stats = await self.player_repository.get_player_stats(summoner_id)
        if not stats:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Player stats not found"
            )
        return stats
    
    async def get_match_history(self, user_id: str, count: int = 20) -> List[str]:
        """Get player's match history"""
        # Get summoner
        summoner = await self.get_summoner(user_id)
        
        # Validate PUUID
        try:
            self.player_domain.validate_puuid(summoner.puuid)
        except DomainException as e:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=e.message)
        
        # Get match history
        return await self.player_repository.get_match_history(summoner.puuid, count)
    
    async def sync_match_history(self, puuid: str, region: str, max_matches: int = None) -> int:
        """
        Sync match history for a player - fetches new matches up to max_matches.
        Public method that can be called from routes or other services.
        
        Args:
            puuid: Player's PUUID
            region: Regional routing value
            max_matches: Maximum number of matches to sync (None for all matches)
            
        Returns:
            Number of new matches saved
        """
        if max_matches:
            logger.info(f"Starting match history sync for {puuid} (max {max_matches} matches)")
            saved_count = await self._sync_matches_with_limit(puuid, region, max_matches)
        else:
            logger.info(f"Starting match history sync for {puuid} (all matches)")
            saved_count = await self.match_repository.sync_player_matches(puuid, region, self.riot_api)
        
        logger.info(f"Match history sync complete: {saved_count} new matches")
        return saved_count
    
    async def sync_initial_matches(self, puuid: str, region: str, count: int = 10) -> List[RecentGameSummary]:
        """
        Sync initial matches for immediate display (non-blocking).
        
        Args:
            puuid: Player's PUUID
            region: Regional routing value
            count: Number of matches to fetch (default 10)
            
        Returns:
            List of game summaries
        """
        logger.info(f"Syncing initial {count} matches for {puuid}")
        
        # Fetch match IDs
        match_ids = await self.riot_api.get_match_ids_by_puuid(puuid, region, count=count, start=0)
        
        if not match_ids:
            return []
        
        # Fetch and build games (checking DB first)
        games = await self.player_repository.fetch_and_build_games(match_ids, puuid, region)
        
        logger.info(f"Synced {len(games)} initial matches")
        return games
    
    async def _sync_all_matches_with_rate_limit(self, puuid: str, region: str) -> None:
        """
        Background task to sync remaining matches (up to 100 total).
        Rate limiting is handled automatically by RiotAPIConfig.
        Runs asynchronously without blocking the response.
        """
        import asyncio
        
        try:
            max_total_matches = 100  # Cap at 100 matches total
            logger.info(f"Background sync: Starting to fetch up to {max_total_matches} total matches for {puuid}")
            
            total_saved = 0
            start_index = 10  # Skip first 10 (already fetched)
            batch_size = 100  # Larger batches - rate limiter handles throttling
            
            while start_index < max_total_matches:
                # Check if we've reached the cap
                remaining = max_total_matches - start_index
                if remaining <= 0:
                    logger.info(f"Background sync: Reached {max_total_matches} match cap")
                    break
                
                # Adjust batch size if near the cap
                current_batch_size = min(batch_size, remaining)
                
                # Fetch batch of match IDs
                logger.info(f"Background: Fetching match IDs starting at index {start_index} (batch size: {current_batch_size})")
                match_ids = await self.riot_api.get_match_ids_by_puuid(
                    puuid, region, count=current_batch_size, start=start_index
                )
                
                if not match_ids or len(match_ids) == 0:
                    logger.info(f"Background sync complete: No more matches found ({total_saved} total saved)")
                    break
                
                logger.info(f"Background: Processing {len(match_ids)} matches")
                
                # Process each match with a small delay
                batch_saved = 0
                should_stop = False
                
                for i, match_id in enumerate(match_ids):
                    # Check if match already exists
                    exists = await self.match_repository.match_exists(match_id)
                    
                    if exists:
                        logger.info(f"Background: Match {match_id} exists - stopping ({total_saved} total saved)")
                        should_stop = True
                        break
                    
                    # Fetch and save match
                    logger.info(f"Background: Fetching match {start_index + i + 1}: {match_id}")
                    match_data = await self.riot_api.get_match_details(match_id, region)
                    
                    if match_data:
                        # Save full match data
                        if await self.match_repository.save_match(match_id, match_data):
                            batch_saved += 1
                            total_saved += 1
                            logger.info(f"Background: Saved match {match_id} ({total_saved} total)")
                
                if should_stop:
                    break
                
                # Update recent_games cache with all matches fetched so far
                if batch_saved > 0:
                    # Calculate total matches processed so far
                    total_processed = start_index + len(match_ids)
                    logger.info(f"Background: Updating cache with {total_processed} total matches")
                    
                    # Fetch all match IDs up to current position
                    all_match_ids = await self.riot_api.get_match_ids_by_puuid(puuid, region, count=total_processed, start=0)
                    
                    # Get all games from DB
                    all_games = await self.player_repository.get_matches_from_db(all_match_ids, puuid)
                    
                    # Update cache
                    await self.player_repository.update_recent_games_cache(puuid, all_games)
                    logger.info(f"Background: Updated cache with {len(all_games)} games")
                
                # If we got fewer matches than requested, we've reached the end
                if len(match_ids) < current_batch_size:
                    logger.info(f"Background sync complete: Reached end of history ({total_saved} total saved)")
                    break
                
                # Move to next batch
                start_index += batch_size
            
            # Final cache update with all matches (up to 200)
            logger.info(f"Background sync finished: {total_saved} total matches saved")
            
            try:
                all_match_ids = await self.riot_api.get_match_ids_by_puuid(puuid, region, count=max_total_matches, start=0)
                all_games = await self.player_repository.get_matches_from_db(all_match_ids, puuid)
                await self.player_repository.update_recent_games_cache(puuid, all_games)
                logger.info(f"Background: Final cache update with {len(all_games)} total games (capped at {max_total_matches})")
            except Exception as cache_error:
                logger.error(f"Error updating final cache: {cache_error}")
            
        except Exception as e:
            logger.error(f"Error in background match sync for {puuid}: {e}")
    
    async def _sync_matches_with_limit(self, puuid: str, region: str, max_matches: int) -> int:
        """
        Sync matches with a limit on total matches to fetch.
        
        Args:
            puuid: Player's PUUID
            region: Regional routing value
            max_matches: Maximum number of matches to sync
            
        Returns:
            Number of new matches saved
        """
        try:
            # Check if already synced
            if await self.match_repository.is_match_history_synced(puuid, region, self.riot_api):
                logger.info(f"Match history already up to date for {puuid}")
                return 0
            
            # Fetch match IDs (limited)
            logger.info(f"Fetching up to {max_matches} match IDs")
            match_ids = await self.riot_api.get_match_ids_by_puuid(puuid, region, count=max_matches, start=0)
            
            if not match_ids:
                logger.warning(f"No match IDs found for {puuid}")
                return 0
            
            logger.info(f"Found {len(match_ids)} match IDs to process")
            
            # Process matches
            saved_count = 0
            for i, match_id in enumerate(match_ids):
                # Check if match already exists
                exists = await self.match_repository.match_exists(match_id)
                
                if exists:
                    logger.info(f"Match {match_id} already exists - stopping sync ({saved_count} saved)")
                    break
                
                # Fetch and save match
                logger.info(f"Fetching match {i+1}/{len(match_ids)}: {match_id}")
                match_data = await self.riot_api.get_match_details(match_id, region)
                
                if not match_data:
                    logger.warning(f"Could not fetch match details for: {match_id}")
                    continue
                
                # Save to database
                if await self.match_repository.save_match(match_id, match_data):
                    saved_count += 1
                    logger.info(f"Saved match {match_id} ({saved_count} total)")
                else:
                    logger.error(f"Failed to save match: {match_id}")
            
            return saved_count
            
        except Exception as e:
            logger.error(f"Error syncing matches for {puuid}: {e}")
            return 0
    
    async def is_match_history_synced(self, puuid: str, region: str) -> bool:
        """
        Check if player's match history is already synced.
        Public method for checking sync status.
        
        Args:
            puuid: Player's PUUID
            region: Regional routing value
            
        Returns:
            True if synced, False otherwise
        """
        return await self.match_repository.is_match_history_synced(puuid, region, self.riot_api)
    
    async def get_recent_games(self, user_id: str, count: int = 5) -> List[RecentGameSummary]:
        """
        Get player's recent games with smart caching strategy:
        1. Check first match ID (1 API call)
        2. Check recent_games cache - if match, return cache
        3. Check matches DB - if exists, query DB
        4. Fallback: fetch from API
        """
        logger.info(f"Fetching recent games for user: {user_id}")
        
        # Get user's PUUID and region from DB only (don't fetch fresh summoner data)
        user_summoner = await self.player_repository.get_user_summoner_basic(user_id)
        
        if not user_summoner:
            logger.warning(f"No summoner linked for user: {user_id}")
            return []
        
        puuid = user_summoner.get('puuid')
        region = user_summoner.get('region')
        
        logger.info(f"Fetching recent games for PUUID: {puuid}")
        
        # Step 1: Get first match ID to check freshness
        first_match_ids = await self.riot_api.get_match_ids_by_puuid(puuid, region, count=1)
        
        if not first_match_ids:
            logger.info("No recent matches found")
            return []
        
        first_match_id = first_match_ids[0]
        logger.info(f"First match ID: {first_match_id}")
        
        # Step 2: Check recent_games cache
        cached_games = await self.player_repository.get_cached_recent_games(puuid, count)
        
        if cached_games and len(cached_games) > 0:
            if cached_games[0].match_id == first_match_id and len(cached_games) >= count:
                logger.info(f"✅ Cache hit! Returning {len(cached_games)} cached games")
                return cached_games
            else:
                if cached_games[0].match_id != first_match_id:
                    logger.info(f"Cache miss - first match changed")
                else:
                    logger.info(f"Cache incomplete - has {len(cached_games)} but need {count}")
        
        # Step 3: Check if first match exists in matches DB
        first_match_data = await self.player_repository.get_match_from_db(first_match_id)
        
        if first_match_data:
            # Matches are in DB, query from there
            logger.info(f"✅ First match in DB - querying all from DB")
            match_ids = await self.riot_api.get_match_ids_by_puuid(puuid, region, count)
            games = await self.player_repository.get_matches_from_db(match_ids, puuid)
            
            # Update cache
            await self.player_repository.update_recent_games_cache(puuid, games)
            return games
        
        # Step 4: Fetch from API (checking DB for each match)
        logger.info(f"First match not in DB - fetching with API fallback")
        match_ids = await self.riot_api.get_match_ids_by_puuid(puuid, region, count)
        games = await self.player_repository.fetch_and_build_games(match_ids, puuid, region)
        
        # Update cache
        await self.player_repository.update_recent_games_cache(puuid, games)
        return games
