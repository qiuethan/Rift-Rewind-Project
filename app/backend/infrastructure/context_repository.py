"""
Context Repository Implementation - Supabase
Clean Architecture - Layer 5 (Infrastructure)
"""
from typing import Optional, Dict, Any
from repositories.context_repository import ContextRepository
from infrastructure.database.database_client import DatabaseClient
from constants.database import DatabaseTable
from utils.logger import logger


class ContextRepositorySupabase(ContextRepository):
    """Supabase implementation of context repository"""
    
    def __init__(self, db: DatabaseClient):
        """
        Initialize context repository
        
        Args:
            db: Database client for data access
        """
        self.db = db
    
    async def get_summoner_context(self, puuid: str) -> Optional[Dict[str, Any]]:
        """
        Retrieve basic summoner info from summoners table
        
        Args:
            puuid: Player UUID
            
        Returns:
            Dict with game_name and region, or None if not found
        """
        try:
            logger.info(f"Querying summoners table for PUUID: {puuid}")
            result = await self.db.table(DatabaseTable.SUMMONERS).select(
                'game_name, region'
            ).eq('puuid', puuid).limit(1).execute()
            
            logger.info(f"Query result: {result.data if result else 'None'}")
            
            if result.data and len(result.data) > 0:
                user_data = result.data[0]
                logger.info(f"Retrieved summoner context for {puuid}: {user_data.get('game_name')} ({user_data.get('region')})")
                return {
                    'game_name': user_data.get('game_name'),
                    'region': user_data.get('region')
                }
            
            logger.warning(f"No summoner context found for PUUID: {puuid}")
            return None
            
        except Exception as e:
            logger.error(f"Error retrieving summoner context: {e}")
            return None
    
    async def get_champion_progress_context(self, puuid: str, champion_id: int) -> Optional[Dict[str, Any]]:
        """
        Retrieve champion progress data from champion_progress table
        
        Args:
            puuid: Player UUID
            champion_id: Champion ID
            
        Returns:
            Dict with champion progress stats, or None if not found
        """
        try:
            logger.info(f"Querying champion_progress for PUUID: {puuid}, Champion ID: {champion_id}")
            result = await self.db.table(DatabaseTable.CHAMPION_PROGRESS).select(
                'champion_name, total_games, wins, losses, win_rate, avg_eps_score, avg_cps_score, avg_kda, eps_trend, cps_trend, recent_trend'
            ).eq('puuid', puuid).eq('champion_id', champion_id).limit(1).execute()
            
            logger.info(f"Champion progress query result: {result.data if result else 'None'}")
            
            if result.data and len(result.data) > 0:
                progress_data = result.data[0]
                logger.info(f"Retrieved champion progress for {puuid} on {progress_data.get('champion_name')}")
                return {
                    'champion_name': progress_data.get('champion_name'),
                    'total_games': progress_data.get('total_games'),
                    'win_rate': progress_data.get('win_rate'),
                    'avg_eps_score': progress_data.get('avg_eps_score'),
                    'avg_cps_score': progress_data.get('avg_cps_score'),
                    'eps_trend': progress_data.get('eps_trend'),
                    'cps_trend': progress_data.get('cps_trend'),
                    'recent_trend': progress_data.get('recent_trend')
                }
            
            logger.warning(f"No champion progress found for PUUID: {puuid}, Champion: {champion_id}")
            return None
            
        except Exception as e:
            logger.error(f"Error retrieving champion progress context: {e}")
            return None
    
    async def get_match_context(self, puuid: str, match_id: str) -> Optional[Dict[str, Any]]:
        """
        Retrieve match information from matches table
        
        Args:
            puuid: Player UUID
            match_id: Match ID
            
        Returns:
            Dict with match info (game_type, player's champion, analysis), or None if not found
        """
        try:
            logger.info(f"Querying matches table for match_id: {match_id}, puuid: {puuid}")
            
            # First check if match exists at all (debug)
            check_result = await self.db.table(DatabaseTable.MATCHES).select('match_id').eq('match_id', match_id).limit(1).execute()
            logger.info(f"Match exists check: {len(check_result.data) if check_result and check_result.data else 0} records")
            
            result = await self.db.table(DatabaseTable.MATCHES).select(
                'match_data, analysis'
            ).eq('match_id', match_id).limit(1).execute()
            
            logger.info(f"Match query completed. Found: {len(result.data) if result and result.data else 0} records")
            
            if result.data and len(result.data) > 0:
                match_record = result.data[0]
                match_data = match_record.get('match_data', {})
                analysis = match_record.get('analysis')
                
                info = match_data.get('info', {})
                game_type = info.get('gameMode', 'Unknown')
                game_duration = info.get('gameDuration', 0)
                
                # Find player's champion and stats
                player_champion = None
                player_stats = None
                for participant in info.get('participants', []):
                    if participant.get('puuid') == puuid:
                        player_champion = participant.get('championName')
                        player_stats = {
                            'win': participant.get('win', False),
                            'kills': participant.get('kills', 0),
                            'deaths': participant.get('deaths', 0),
                            'assists': participant.get('assists', 0),
                            'damage': participant.get('totalDamageDealtToChampions', 0),
                            'gold': participant.get('goldEarned', 0),
                            'cs': participant.get('totalMinionsKilled', 0)
                        }
                        break
                
                logger.info(f"Retrieved match context for {match_id}: {player_champion} in {game_type}")
                
                return {
                    'game_type': game_type,
                    'game_duration': game_duration,
                    'player_champion': player_champion,
                    'player_stats': player_stats,
                    'analysis': analysis
                }
            
            logger.warning(f"No match found for match_id: {match_id}")
            return None
            
        except Exception as e:
            logger.error(f"Error retrieving match context: {e}")
            return None
