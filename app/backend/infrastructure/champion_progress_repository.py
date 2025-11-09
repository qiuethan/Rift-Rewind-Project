"""
Champion Progress Repository Implementation with Supabase
Following Clean Architecture: Returns None on failure, no HTTPException
"""
from repositories.champion_progress_repository import ChampionProgressRepository
from models.champion_progress import (
    ChampionProgressResponse,
    AllChampionsProgressResponse,
    ChampionProgressRecord,
    ChampionProgressTrend,
    ChampionMatchScore,
    UpdateChampionProgressRequest
)
from infrastructure.database.database_client import DatabaseClient
from constants.database import DatabaseTable
from typing import Optional, List
from utils.logger import logger
from datetime import datetime


class ChampionProgressRepositorySupabase(ChampionProgressRepository):
    """Supabase implementation of champion progress repository"""
    
    def __init__(self, db: DatabaseClient):
        """
        Initialize repository with database client
        
        Args:
            db: Database abstraction for data persistence
        """
        self.db = db
        logger.info("Champion progress repository initialized with Supabase")
    
    async def get_champion_progress(
        self, 
        user_id: str, 
        champion_id: int, 
        limit: int
    ) -> Optional[ChampionProgressResponse]:
        """Get progress data for a specific champion"""
        try:
            logger.info(f"Fetching champion progress for user_id='{user_id}', champion_id={champion_id}")
            
            # Get champion progress record
            result = await self.db.table(DatabaseTable.CHAMPION_PROGRESS).select('*').eq(
                'user_id', user_id
            ).eq('champion_id', champion_id).limit(1).execute()
            
            logger.info(f"Query result: {result.data}")
            
            if not result.data or len(result.data) == 0:
                logger.warning(f"No progress data found for user_id='{user_id}', champion_id={champion_id}")
                # Debug: Check what's actually in the table
                all_records = await self.db.table(DatabaseTable.CHAMPION_PROGRESS).select('user_id, champion_id, champion_name').limit(5).execute()
                logger.info(f"Sample records in champion_progress table: {all_records.data}")
                return None
            
            record_data = result.data[0]
            
            # Build trend
            trend = ChampionProgressTrend(
                champion_id=record_data['champion_id'],
                champion_name=record_data['champion_name'],
                total_games=record_data['total_games'],
                wins=record_data['wins'],
                losses=record_data['losses'],
                win_rate=record_data['win_rate'],
                avg_eps_score=record_data['avg_eps_score'],
                avg_cps_score=record_data['avg_cps_score'],
                avg_kda=record_data['avg_kda'],
                recent_trend=record_data.get('recent_trend', 'stable'),
                eps_trend=record_data.get('eps_trend', 'stable'),
                cps_trend=record_data.get('cps_trend', 'stable'),
                last_played=record_data['last_played'],
                mastery_level=record_data.get('mastery_level'),
                mastery_points=record_data.get('mastery_points')
            )
            
            # Build recent matches (limit to requested amount)
            recent_matches_data = record_data.get('recent_matches', [])[:limit]
            recent_matches = [ChampionMatchScore(**match) for match in recent_matches_data]
            
            response = ChampionProgressResponse(
                user_id=user_id,
                champion_id=champion_id,
                champion_name=record_data['champion_name'],
                trend=trend,
                recent_matches=recent_matches,
                performance_summary={
                    'history': record_data.get('performance_history', []),
                    'total_data_points': len(record_data.get('performance_history', []))
                }
            )
            
            logger.info(f"Successfully fetched progress for champion {champion_id}")
            return response
            
        except Exception as e:
            logger.error(f"Error fetching champion progress: {e}")
            return None
    
    async def get_all_champions_progress(
        self, 
        user_id: str
    ) -> Optional[AllChampionsProgressResponse]:
        """Get progress data for all champions"""
        try:
            logger.info(f"Fetching all champions progress for user {user_id}")
            
            result = await self.db.table(DatabaseTable.CHAMPION_PROGRESS).select('*').eq(
                'user_id', user_id
            ).order('total_games', desc=True).execute()
            
            if not result.data or len(result.data) == 0:
                logger.info(f"No champion progress data found for user {user_id}")
                return None
            
            # Build trends for all champions
            champions = []
            for record in result.data:
                trend = ChampionProgressTrend(
                    champion_id=record['champion_id'],
                    champion_name=record['champion_name'],
                    total_games=record['total_games'],
                    wins=record['wins'],
                    losses=record['losses'],
                    win_rate=record['win_rate'],
                    avg_eps_score=record['avg_eps_score'],
                    avg_cps_score=record['avg_cps_score'],
                    avg_kda=record['avg_kda'],
                    recent_trend=record['recent_trend'],
                    last_played=record['last_played'],
                    mastery_level=record.get('mastery_level'),
                    mastery_points=record.get('mastery_points')
                )
                champions.append(trend)
            
            # Find most played (already sorted by total_games desc)
            most_played = champions[0] if champions else None
            
            # Find best performing (highest avg_eps_score)
            best_performing = max(champions, key=lambda c: c.avg_eps_score) if champions else None
            
            response = AllChampionsProgressResponse(
                user_id=user_id,
                champions=champions,
                total_champions_played=len(champions),
                most_played_champion=most_played,
                best_performing_champion=best_performing
            )
            
            logger.info(f"Successfully fetched progress for {len(champions)} champions")
            return response
            
        except Exception as e:
            logger.error(f"Error fetching all champions progress: {e}")
            return None
    
    async def update_champion_progress(
        self,
        user_id: str,
        puuid: str,
        update_request: UpdateChampionProgressRequest
    ) -> Optional[ChampionProgressRecord]:
        """Update champion progress after a match"""
        try:
            logger.info(f"Updating champion progress for user {user_id}, champion {update_request.champion_id}")
            
            # Get existing record
            existing = await self.get_champion_progress_record(user_id, update_request.champion_id)
            
            # Build new match score
            new_match = {
                'match_id': update_request.match_id,
                'champion_id': update_request.champion_id,
                'champion_name': update_request.champion_name,
                'game_date': update_request.game_date,
                'eps_score': update_request.eps_score,
                'cps_score': update_request.cps_score,
                'kda': update_request.kda,
                'win': update_request.win,
                'kills': update_request.kills,
                'deaths': update_request.deaths,
                'assists': update_request.assists,
                'cs': update_request.cs,
                'gold': update_request.gold,
                'damage': update_request.damage,
                'vision_score': update_request.vision_score
            }
            
            if existing:
                # Update existing record
                recent_matches = existing.recent_matches or []
                recent_matches.insert(0, new_match)  # Add to front
                recent_matches = recent_matches[:50]  # Keep last 50 matches
                
                performance_history = existing.performance_history or []
                performance_history.insert(0, {
                    'date': update_request.game_date,
                    'eps_score': update_request.eps_score,
                    'cps_score': update_request.cps_score
                })
                performance_history = performance_history[:100]  # Keep last 100
                
                # Calculate new averages
                total_games = existing.total_games + 1
                wins = existing.wins + (1 if update_request.win else 0)
                losses = existing.losses + (0 if update_request.win else 1)
                
                # Running average for scores
                avg_eps_score = ((existing.avg_eps_score * existing.total_games) + update_request.eps_score) / total_games
                avg_cps_score = ((existing.avg_cps_score * existing.total_games) + update_request.cps_score) / total_games
                avg_kda = ((existing.avg_kda * existing.total_games) + update_request.kda) / total_games
                
                win_rate = (wins / total_games) * 100 if total_games > 0 else 0.0
                
                # Determine separate trends for EPS and CPS
                recent_eps_scores = [m.get('eps_score', 0) for m in recent_matches[:10]]
                recent_cps_scores = [m.get('cps_score', 0) for m in recent_matches[:10]]
                eps_trend = self._calculate_trend(recent_eps_scores)
                cps_trend = self._calculate_trend(recent_cps_scores)
                # Keep combined trend for backward compatibility
                combined_trend = self._calculate_combined_trend(recent_eps_scores, recent_cps_scores)
                
                updated_record = ChampionProgressRecord(
                    id=existing.id,
                    user_id=user_id,
                    puuid=puuid,
                    champion_id=update_request.champion_id,
                    champion_name=update_request.champion_name,
                    total_games=total_games,
                    wins=wins,
                    losses=losses,
                    win_rate=round(win_rate, 2),
                    avg_eps_score=round(avg_eps_score, 2),
                    avg_cps_score=round(avg_cps_score, 2),
                    avg_kda=round(avg_kda, 2),
                    recent_trend=combined_trend,
                    eps_trend=eps_trend,
                    cps_trend=cps_trend,
                    last_played=update_request.game_date,
                    recent_matches=recent_matches,
                    performance_history=performance_history
                )
                
                # Update in database
                result = await self.db.table(DatabaseTable.CHAMPION_PROGRESS).update(
                    updated_record.to_db_dict()
                ).eq('user_id', user_id).eq('champion_id', update_request.champion_id).execute()
                
                logger.info(f"Updated champion progress for champion {update_request.champion_id}")
                return updated_record
                
            else:
                # Create new record
                new_record = ChampionProgressRecord(
                    user_id=user_id,
                    puuid=puuid,
                    champion_id=update_request.champion_id,
                    champion_name=update_request.champion_name,
                    total_games=1,
                    wins=1 if update_request.win else 0,
                    losses=0 if update_request.win else 1,
                    win_rate=100.0 if update_request.win else 0.0,
                    avg_eps_score=update_request.eps_score,
                    avg_cps_score=update_request.cps_score,
                    avg_kda=update_request.kda,
                    recent_trend="stable",
                    last_played=update_request.game_date,
                    recent_matches=[new_match],
                    performance_history=[{
                        'date': update_request.game_date,
                        'eps_score': update_request.eps_score,
                        'cps_score': update_request.cps_score
                    }]
                )
                
                return await self.create_champion_progress_record(new_record)
                
        except Exception as e:
            logger.error(f"Error updating champion progress: {e}")
            return None
    
    def _calculate_trend(self, recent_scores: List[float]) -> str:
        """Helper to calculate trend from recent scores"""
        if len(recent_scores) < 5:
            return "stable"
        
        # Compare first half vs second half
        mid = len(recent_scores) // 2
        first_half_avg = sum(recent_scores[mid:]) / (len(recent_scores) - mid)
        second_half_avg = sum(recent_scores[:mid]) / mid
        
        if first_half_avg == 0:
            return "stable"
        
        diff_percentage = ((second_half_avg - first_half_avg) / first_half_avg) * 100
        
        if diff_percentage > 5:
            return "improving"
        elif diff_percentage < -5:
            return "declining"
        else:
            return "stable"
    
    def _calculate_combined_trend(self, eps_scores: List[float], cps_scores: List[float]) -> str:
        """
        Calculate trend based on both EPS and CPS scores
        EPS measures efficiency (CS, gold, vision, damage)
        CPS measures combat performance (kills, deaths, assists, KDA)
        """
        if len(eps_scores) < 5 or len(cps_scores) < 5:
            return "stable"
        
        # Calculate trend for both metrics
        eps_trend = self._calculate_trend(eps_scores)
        cps_trend = self._calculate_trend(cps_scores)
        
        # If both are improving or declining, return that
        if eps_trend == cps_trend:
            return eps_trend
        
        # If one is improving and one is declining, check which has stronger signal
        mid = len(eps_scores) // 2
        
        # EPS trend strength
        eps_first_half = sum(eps_scores[mid:]) / (len(eps_scores) - mid)
        eps_second_half = sum(eps_scores[:mid]) / mid
        eps_diff = ((eps_second_half - eps_first_half) / eps_first_half * 100) if eps_first_half > 0 else 0
        
        # CPS trend strength
        cps_first_half = sum(cps_scores[mid:]) / (len(cps_scores) - mid)
        cps_second_half = sum(cps_scores[:mid]) / mid
        cps_diff = ((cps_second_half - cps_first_half) / cps_first_half * 100) if cps_first_half > 0 else 0
        
        # Average the two trends
        avg_diff = (eps_diff + cps_diff) / 2
        
        if avg_diff > 5:
            return "improving"
        elif avg_diff < -5:
            return "declining"
        else:
            return "stable"
    
    async def get_champion_progress_record(
        self,
        user_id: str,
        champion_id: int
    ) -> Optional[ChampionProgressRecord]:
        """Get raw champion progress record"""
        try:
            result = await self.db.table(DatabaseTable.CHAMPION_PROGRESS).select('*').eq(
                'user_id', user_id
            ).eq('champion_id', champion_id).limit(1).execute()
            
            if not result.data or len(result.data) == 0:
                return None
            
            return ChampionProgressRecord(**result.data[0])
            
        except Exception as e:
            logger.error(f"Error fetching champion progress record: {e}")
            return None
    
    async def create_champion_progress_record(
        self,
        record: ChampionProgressRecord
    ) -> Optional[ChampionProgressRecord]:
        """Create a new champion progress record"""
        try:
            logger.info(f"Creating new champion progress record for champion {record.champion_id}")
            
            result = await self.db.table(DatabaseTable.CHAMPION_PROGRESS).insert(
                record.to_db_dict()
            ).execute()
            
            if result.data and len(result.data) > 0:
                logger.info(f"Successfully created champion progress record")
                return ChampionProgressRecord(**result.data[0])
            
            return None
            
        except Exception as e:
            logger.error(f"Error creating champion progress record: {e}")
            return None
    
    async def delete_champion_progress(
        self,
        user_id: str,
        champion_id: Optional[int] = None
    ) -> bool:
        """Delete champion progress data"""
        try:
            query = self.db.table(DatabaseTable.CHAMPION_PROGRESS).delete().eq('user_id', user_id)
            
            if champion_id is not None:
                query = query.eq('champion_id', champion_id)
                logger.info(f"Deleting champion progress for user {user_id}, champion {champion_id}")
            else:
                logger.info(f"Deleting all champion progress for user {user_id}")
            
            await query.execute()
            logger.info("Successfully deleted champion progress")
            return True
            
        except Exception as e:
            logger.error(f"Error deleting champion progress: {e}")
            return False
