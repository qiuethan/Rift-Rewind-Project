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
        Retrieve comprehensive match information including all details
        
        Args:
            puuid: Player UUID
            match_id: Match ID
            
        Returns:
            Dict with comprehensive match data including teams, stats, analysis, timeline, or None if not found
        """
        try:
            logger.info(f"Querying matches table for comprehensive match data: {match_id}, puuid: {puuid}")
            
            result = await self.db.table(DatabaseTable.MATCHES).select(
                'match_data, analysis, timeline_data, game_mode, game_version, queue_id, game_duration'
            ).eq('match_id', match_id).limit(1).execute()
            
            logger.info(f"Match query completed. Found: {len(result.data) if result and result.data else 0} records")
            
            if result.data and len(result.data) > 0:
                match_record = result.data[0]
                match_data = match_record.get('match_data', {})
                info = match_data.get('info', {})
                
                # Extract all participants with full details
                participants = info.get('participants', [])
                all_participants = []
                player_champion = None
                player_stats = None
                player_team_id = None
                
                for participant in participants:
                    champ_name = participant.get('championName')
                    team_id = participant.get('teamId')
                    
                    participant_info = {
                        'champion': champ_name,
                        'summoner': participant.get('summonerName'),
                        'team_id': team_id,
                        'role': participant.get('teamPosition'),
                        'kills': participant.get('kills', 0),
                        'deaths': participant.get('deaths', 0),
                        'assists': participant.get('assists', 0)
                    }
                    all_participants.append(participant_info)
                    
                    if participant.get('puuid') == puuid:
                        player_champion = champ_name
                        player_team_id = team_id
                        player_stats = {
                            'win': participant.get('win', False),
                            'kills': participant.get('kills', 0),
                            'deaths': participant.get('deaths', 0),
                            'assists': participant.get('assists', 0),
                            'damage': participant.get('totalDamageDealtToChampions', 0),
                            'gold': participant.get('goldEarned', 0),
                            'cs': participant.get('totalMinionsKilled', 0),
                            'role': participant.get('teamPosition')
                        }
                
                # Split into your team and enemy team
                your_team = [p for p in all_participants if p['team_id'] == player_team_id]
                enemy_team = [p for p in all_participants if p['team_id'] != player_team_id]
                
                logger.info(f"Retrieved comprehensive match context for {match_id}: {player_champion} in {match_record.get('game_mode')}")
                
                return {
                    'game_type': match_record.get('game_mode', 'Unknown'),
                    'game_mode': match_record.get('game_mode'),
                    'game_version': match_record.get('game_version'),
                    'queue_id': match_record.get('queue_id'),
                    'game_duration': match_record.get('game_duration', 0),
                    'player_champion': player_champion,
                    'player_stats': player_stats,
                    'your_team': your_team,
                    'enemy_team': enemy_team,
                    'all_participants': all_participants,
                    'analysis': match_record.get('analysis'),
                    'timeline_data': match_record.get('timeline_data')
                }
            
            logger.warning(f"No match found for match_id: {match_id}")
            return None
            
        except Exception as e:
            logger.error(f"Error retrieving match context: {e}")
            return None
    
    async def get_summoner_overview(self, puuid: str) -> Optional[Dict[str, Any]]:
        """
        Retrieve comprehensive summoner profile with mastery and recent games
        
        Args:
            puuid: Player UUID
            
        Returns:
            Dict with full profile including masteries and recent games, or None if not found
        """
        try:
            logger.info(f"Querying summoners table for full overview: {puuid}")
            result = await self.db.table(DatabaseTable.SUMMONERS).select(
                'game_name, region, summoner_level, profile_icon_id, champion_masteries, total_mastery_score, recent_games'
            ).eq('puuid', puuid).limit(1).execute()
            
            if result.data and len(result.data) > 0:
                summoner_data = result.data[0]
                champion_masteries = summoner_data.get('champion_masteries', [])
                recent_games = summoner_data.get('recent_games', [])
                
                # Extract top 5 champions from masteries
                top_champions = []
                if isinstance(champion_masteries, list):
                    top_champions = sorted(
                        champion_masteries,
                        key=lambda x: x.get('championPoints', 0),
                        reverse=True
                    )[:5]
                
                logger.info(f"Retrieved summoner overview for {puuid}")
                return {
                    'game_name': summoner_data.get('game_name'),
                    'region': summoner_data.get('region'),
                    'summoner_level': summoner_data.get('summoner_level', 0),
                    'profile_icon_id': summoner_data.get('profile_icon_id', 0),
                    'total_mastery_score': summoner_data.get('total_mastery_score', 0),
                    'top_champions': top_champions,
                    'recent_games': recent_games if isinstance(recent_games, list) else [],
                    'total_champions_played': len(champion_masteries) if isinstance(champion_masteries, list) else 0
                }
            
            logger.warning(f"No summoner overview found for PUUID: {puuid}")
            return None
            
        except Exception as e:
            logger.error(f"Error retrieving summoner overview: {e}")
            return None
    
    async def get_champion_detailed(self, puuid: str, champion_id: int) -> Optional[Dict[str, Any]]:
        """
        Retrieve detailed champion data including recent matches and performance history
        
        Args:
            puuid: Player UUID
            champion_id: Champion ID
            
        Returns:
            Dict with detailed champion stats and history, or None if not found
        """
        try:
            logger.info(f"Querying champion_progress for detailed data: {puuid}, Champion ID: {champion_id}")
            result = await self.db.table(DatabaseTable.CHAMPION_PROGRESS).select(
                'champion_name, total_games, wins, losses, win_rate, avg_eps_score, avg_cps_score, avg_kda, '
                'eps_trend, cps_trend, recent_trend, mastery_level, mastery_points, recent_matches, performance_history'
            ).eq('puuid', puuid).eq('champion_id', champion_id).limit(1).execute()
            
            if result.data and len(result.data) > 0:
                progress_data = result.data[0]
                recent_matches = progress_data.get('recent_matches', [])
                performance_history = progress_data.get('performance_history', [])
                
                # Find best and worst games from recent matches
                best_game = None
                worst_game = None
                if isinstance(recent_matches, list) and len(recent_matches) > 0:
                    sorted_by_eps = sorted(
                        [m for m in recent_matches if isinstance(m, dict) and 'eps_score' in m],
                        key=lambda x: x.get('eps_score', 0),
                        reverse=True
                    )
                    if sorted_by_eps:
                        best_game = sorted_by_eps[0]
                        worst_game = sorted_by_eps[-1]
                
                logger.info(f"Retrieved detailed champion data for {puuid} on {progress_data.get('champion_name')}")
                return {
                    'champion_name': progress_data.get('champion_name'),
                    'total_games': progress_data.get('total_games'),
                    'wins': progress_data.get('wins'),
                    'losses': progress_data.get('losses'),
                    'win_rate': progress_data.get('win_rate'),
                    'avg_eps_score': progress_data.get('avg_eps_score'),
                    'avg_cps_score': progress_data.get('avg_cps_score'),
                    'avg_kda': progress_data.get('avg_kda'),
                    'eps_trend': progress_data.get('eps_trend'),
                    'cps_trend': progress_data.get('cps_trend'),
                    'recent_trend': progress_data.get('recent_trend'),
                    'mastery_level': progress_data.get('mastery_level'),
                    'mastery_points': progress_data.get('mastery_points'),
                    'recent_matches': recent_matches[:10] if isinstance(recent_matches, list) else [],  # Last 10
                    'performance_history': performance_history if isinstance(performance_history, list) else [],
                    'best_game': best_game,
                    'worst_game': worst_game
                }
            
            logger.warning(f"No detailed champion data found for PUUID: {puuid}, Champion: {champion_id}")
            return None
            
        except Exception as e:
            logger.error(f"Error retrieving detailed champion data: {e}")
            return None
    
    
    async def get_recent_performance(self, puuid: str, num_games: int = 10) -> Optional[Dict[str, Any]]:
        """
        Retrieve recent performance summary across last N games
        
        Args:
            puuid: Player UUID
            num_games: Number of recent games to analyze
            
        Returns:
            Dict with recent performance metrics, or None if not found
        """
        try:
            logger.info(f"Querying summoners table for recent games: {puuid}")
            result = await self.db.table(DatabaseTable.SUMMONERS).select(
                'recent_games'
            ).eq('puuid', puuid).limit(1).execute()
            
            if result.data and len(result.data) > 0:
                recent_games = result.data[0].get('recent_games', [])
                
                if not isinstance(recent_games, list) or len(recent_games) == 0:
                    return None
                
                # Analyze last N games
                games_to_analyze = recent_games[:num_games]
                
                total_wins = sum(1 for g in games_to_analyze if g.get('win', False))
                total_games = len(games_to_analyze)
                overall_win_rate = (total_wins / total_games * 100) if total_games > 0 else 0
                
                # Calculate average KDA
                total_kills = sum(g.get('kills', 0) for g in games_to_analyze)
                total_deaths = sum(g.get('deaths', 0) for g in games_to_analyze)
                total_assists = sum(g.get('assists', 0) for g in games_to_analyze)
                avg_kda = ((total_kills + total_assists) / max(total_deaths, 1)) if total_deaths > 0 else total_kills + total_assists
                
                # Most played champions
                champion_counts = {}
                for game in games_to_analyze:
                    champ = game.get('champion', 'Unknown')
                    champion_counts[champ] = champion_counts.get(champ, 0) + 1
                
                most_played = sorted(
                    [{'champion': k, 'games': v} for k, v in champion_counts.items()],
                    key=lambda x: x['games'],
                    reverse=True
                )[:3]
                
                # Find best recent game (by KDA or win)
                best_game = max(games_to_analyze, key=lambda g: (g.get('kills', 0) + g.get('assists', 0)) / max(g.get('deaths', 1), 1))
                
                # Determine current streak
                current_streak = {'type': 'none', 'count': 0}
                if games_to_analyze:
                    streak_type = 'win' if games_to_analyze[0].get('win') else 'loss'
                    streak_count = 0
                    for game in games_to_analyze:
                        if (streak_type == 'win' and game.get('win')) or (streak_type == 'loss' and not game.get('win')):
                            streak_count += 1
                        else:
                            break
                    current_streak = {'type': streak_type, 'count': streak_count}
                
                # Determine trend
                if total_games >= 5:
                    first_half_wins = sum(1 for g in games_to_analyze[total_games//2:] if g.get('win', False))
                    second_half_wins = sum(1 for g in games_to_analyze[:total_games//2] if g.get('win', False))
                    if second_half_wins > first_half_wins:
                        recent_trend = 'improving'
                    elif second_half_wins < first_half_wins:
                        recent_trend = 'declining'
                    else:
                        recent_trend = 'stable'
                else:
                    recent_trend = 'stable'
                
                logger.info(f"Retrieved recent performance for {puuid}")
                return {
                    'last_n_games': total_games,
                    'overall_win_rate': round(overall_win_rate, 1),
                    'total_wins': total_wins,
                    'total_losses': total_games - total_wins,
                    'avg_kda': round(avg_kda, 2),
                    'most_played_champions': most_played,
                    'recent_trend': recent_trend,
                    'best_recent_game': best_game,
                    'current_streak': current_streak
                }
            
            logger.warning(f"No recent performance data found for PUUID: {puuid}")
            return None
            
        except Exception as e:
            logger.error(f"Error retrieving recent performance: {e}")
            return None
