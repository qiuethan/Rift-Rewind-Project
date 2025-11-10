"""
Champion repository implementation
"""
from repositories.champion_repository import ChampionRepository
from models.champions import ChampionData, ChampionRecommendation, AbilitySimilarity
from infrastructure.database.database_client import DatabaseClient
from constants.database import DatabaseTable
from typing import Optional, List, Dict, Any
from utils.logger import logger
from utils.champion_recommender import get_recommender
from utils.champion_mapping import get_graph_name_from_id
import pandas as pd
from pathlib import Path


class ChampionRepositoryImpl(ChampionRepository):
    """Implementation of champion repository"""
    
    # Class-level cache for ability similarity data
    _ability_data_cache: Optional[pd.DataFrame] = None
    _cache_loaded: bool = False
    
    def __init__(self, db: DatabaseClient):
        """Initialize champion repository with database client"""
        self.db = db
        self._load_ability_data()
    
    def _load_ability_data(self):
        """Load ability similarity data from CSV file into cache"""
        if not ChampionRepositoryImpl._cache_loaded:
            try:
                # Path to the CSV file (in project root output folder)
                pq_path = Path(__file__).resolve().parents[3] / 'data' / 'final_comparisons_20251107_194606.parquet'
                # Load CSV with pandas
                ChampionRepositoryImpl._ability_data_cache = pd.read_parquet(pq_path)
                ChampionRepositoryImpl._cache_loaded = True
                print(f"Loaded ability similarity data: {len(ChampionRepositoryImpl._ability_data_cache)} rows")
            except Exception as e:
                print(f"Error loading ability similarity data: {e}")
                ChampionRepositoryImpl._ability_data_cache = pd.DataFrame()
                ChampionRepositoryImpl._cache_loaded = True
    
    def _normalize_champion_name(self, name: str) -> str:
        """Normalize champion name for comparison (handle special characters, case)"""
        # Remove special characters and spaces, lowercase
        normalized = name.lower().replace("'", "").replace(" ", "").replace(".", "")
        return normalized
    
    async def get_ability_similarities(self, champion_id: str, limit_per_ability: int = 3) -> List[AbilitySimilarity]:
        """Get ability similarities for a champion's Q, W, E, R abilities"""
        if ChampionRepositoryImpl._ability_data_cache is None or ChampionRepositoryImpl._ability_data_cache.empty:
            return []
        
        df = ChampionRepositoryImpl._ability_data_cache
        normalized_champion = self._normalize_champion_name(champion_id)
        
        # Find rows where champ1 matches the requested champion
        # Expected CSV columns: champ1, ability1_type, ability1_name, champ2, ability2_type, ability2_name, score, explanation
        champion_abilities = df[
            df['champ1'].str.lower().str.replace("'", "").str.replace(" ", "").str.replace(".", "") == normalized_champion
        ].copy()
        
        if champion_abilities.empty:
            return []
        
        # Group by ability type and get top similarities for each
        abilities = []
        for ability_type in ['Q', 'W', 'E', 'R']:
            ability_matches = champion_abilities[
                champion_abilities['ability1_type'] == ability_type
            ].nlargest(limit_per_ability, 'score')
            
            for _, row in ability_matches.iterrows():
                abilities.append(AbilitySimilarity(
                    ability_type=row['ability1_type'],
                    ability_name=row['ability1_name'],
                    similar_champion=row['champ2'],
                    similar_ability_type=row['ability2_type'],
                    similar_ability_name=row['ability2_name'],
                    similarity_score=float(row['score']),
                    explanation=row['explanation']
                ))
        
        return abilities

    
    async def get_champion_by_id(self, champion_id: str) -> Optional[ChampionData]:
        """Get champion data by ID (DEMO)"""
        # Demo implementation - would query from database
        return ChampionData(
            id=champion_id,
            name=champion_id.capitalize(),
            title="The Demo Champion",
            tags=["Mage", "Assassin"],
            stats={"hp": 500, "attack": 60, "armor": 30},
            abilities=[]
        )
    
    async def get_all_champions(self) -> List[ChampionData]:
        """Get all champion data (DEMO)"""
        # Demo implementation
        demo_champions = ["Ahri", "Lux", "Syndra", "Zed", "Yasuo"]
        return [
            ChampionData(
                id=champ.lower(),
                name=champ,
                title=f"The {champ}",
                tags=["Mage"],
                stats={},
                abilities=[]
            )
            for champ in demo_champions
        ]
    
    async def get_champion_abilities(self, champion_id: str) -> List[Dict[str, Any]]:
        """Get champion abilities (DEMO)"""
        # Demo implementation
        return [
            {"name": "Q - Demo Ability", "description": "Demo description"},
            {"name": "W - Demo Ability", "description": "Demo description"},
            {"name": "E - Demo Ability", "description": "Demo description"},
            {"name": "R - Demo Ultimate", "description": "Demo description"}
        ]
    
    async def calculate_champion_similarity(self, champion_a: str, champion_b: str) -> float:
        """Calculate similarity between two champions using LLM (DEMO)"""
        # Demo implementation - would use LLM API
        return 0.75
    
    async def get_similar_champions(self, champion_id: str, limit: int) -> List[ChampionRecommendation]:
        """
        Get similar champions based on player's champion pool using graph-based recommendations
        weighted by player performance (EPS/CPS).
        
        Args:
            champion_id: Player's PUUID (used to fetch their champion pool)
            limit: Maximum number of recommendations to return
            
        Returns:
            List of ChampionRecommendation objects with similarity scores and reasoning
        """
        try:
            # Get the recommender instance
            recommender = get_recommender()
            
            # Get player's champion pool (list of graph champion names they play)
            puuid = champion_id
            champion_pool = await self.get_player_champion_pool(puuid)
            
            if not champion_pool:
                logger.warning(f"No champion pool found for puuid: {puuid}")
                return []
            
            # Get player's performance metrics for their champion pool
            performance_data = await self.get_player_champion_performance(puuid)
            
            # Get recommendations based on champion pool
            # alpha=0.7 means 70% graph similarity, 30% feature similarity
            recommendations = recommender.recommend_from_champion_pool(
                champion_list=champion_pool,
                top_k=limit * 2,  # Get more candidates for performance re-ranking
                alpha=0.7,
                max_occurrences=0  # Exclude champions played more than twice in pool
            )
            
            # Apply performance-based weighting
            weighted_recommendations = self._apply_performance_weighting(
                recommendations,
                champion_pool,
                performance_data,
                recommender
            )
            
            # Convert to ChampionRecommendation objects
            result = []
            for champ_name, score in weighted_recommendations[:limit]:
                # Normalize score to 0-1 range (scores can be > 1 due to aggregation)
                normalized_score = min(score / len(champion_pool), 1.0)
                
                # Generate reasoning based on champion pool overlap and performance
                reasoning = self._generate_recommendation_reasoning(
                    champ_name, 
                    champion_pool, 
                    recommender,
                    performance_data
                )
                
                result.append(ChampionRecommendation(
                    champion_id=champ_name,
                    champion_name=champ_name,
                    similarity_score=normalized_score,
                    reasoning=reasoning,
                    similar_abilities=None,  # Could be enhanced with ability similarity
                    playstyle_match=self._get_playstyle_match(champ_name, recommender)
                ))
            
            return result
            
        except Exception as e:
            logger.error(f"Error getting similar champions: {e}")
            return []
    
    def _apply_performance_weighting(
        self,
        recommendations: List[tuple],
        champion_pool: List[str],
        performance_data: Dict[str, Dict[str, float]],
        recommender
    ) -> List[tuple]:
        """Apply performance-based weighting to recommendations
        
        Champions similar to high-performing champions in the pool get a boost.
        Weight: 15% performance, 85% base similarity
        """
        if not performance_data:
            return recommendations
        
        # Calculate average performance across player's pool
        pool_performances = [perf for champ, perf in performance_data.items() if champ in champion_pool]
        if not pool_performances:
            return recommendations
        
        avg_pool_eps = sum(p['avg_eps'] for p in pool_performances) / len(pool_performances)
        avg_pool_cps = sum(p['avg_cps'] for p in pool_performances) / len(pool_performances)
        
        weighted_recs = []
        for champ_name, base_score in recommendations:
            # Find which pool champions are most similar to this recommendation
            performance_boost = 0.0
            total_weight = 0.0
            
            for pool_champ in champion_pool:
                if pool_champ not in performance_data:
                    continue
                
                # Get similarity between recommended champ and pool champ
                similarity = 0.0
                if pool_champ in recommender.graph.get(champ_name, {}):
                    similarity = recommender.graph[champ_name][pool_champ]
                
                if similarity > 0.05:  # Only consider significant similarities
                    perf = performance_data[pool_champ]
                    # Normalize EPS/CPS to 0-1 range (assuming max ~100)
                    eps_norm = min(perf['avg_eps'] / 100.0, 1.0)
                    cps_norm = min(perf['avg_cps'] / 100.0, 1.0)
                    
                    # Combined performance score (50% EPS, 50% CPS)
                    perf_score = (eps_norm + cps_norm) / 2.0
                    
                    # Weight by similarity to this pool champion
                    performance_boost += perf_score * similarity
                    total_weight += similarity
            
            # Average the performance boost
            if total_weight > 0:
                performance_boost /= total_weight
            
            # Combine: 85% base similarity, 15% performance weighting
            final_score = (0.85 * base_score) + (0.15 * performance_boost)
            weighted_recs.append((champ_name, final_score))
        
        # Re-sort by weighted score
        weighted_recs.sort(key=lambda x: x[1], reverse=True)
        return weighted_recs
    
    def _generate_recommendation_reasoning(
        self, 
        recommended_champ: str, 
        champion_pool: List[str],
        recommender,
        performance_data: Optional[Dict[str, Dict[str, float]]] = None
    ) -> str:
        """Generate human-readable reasoning for why a champion is recommended"""
        try:
            # Find which champions in the pool are most similar to the recommendation
            similar_to = []
            high_performers = []
            
            for pool_champ in champion_pool[:5]:  # Check top 5 from pool
                if pool_champ in recommender.graph.get(recommended_champ, {}):
                    weight = recommender.graph[recommended_champ][pool_champ]
                    if weight > 0.05:  # Significant similarity threshold
                        similar_to.append(pool_champ)
                        
                        # Check if this is a high-performing champion
                        if performance_data and pool_champ in performance_data:
                            perf = performance_data[pool_champ]
                            if perf['avg_eps'] > 70 or perf['avg_cps'] > 70:
                                high_performers.append(pool_champ)
            
            if high_performers:
                champs_str = ", ".join(high_performers[:2])
                return f"Similar to your high-performing {champs_str}"
            elif similar_to:
                champs_str = ", ".join(similar_to[:3])
                return f"Similar playstyle to your {champs_str}"
            else:
                return "Recommended based on your champion pool"
                
        except Exception as e:
            logger.warning(f"Error generating reasoning: {e}")
            return "Recommended based on your champion pool"
    
    def _get_playstyle_match(self, champion_name: str, recommender) -> Optional[str]:
        """Get playstyle description for a champion based on tags"""
        try:
            if recommender.champ_node_data is None:
                return None
            
            champ_row = recommender.champ_node_data[
                recommender.champ_node_data['championName'] == champion_name
            ]
            
            if champ_row.empty:
                return None
            
            # Extract tags from one-hot encoded columns
            tags = []
            tag_cols = [col for col in champ_row.columns if col.startswith('tag_')]
            for col in tag_cols:
                if champ_row[col].values[0] == 1:
                    tag_name = col.replace('tag_', '')
                    tags.append(tag_name)
            
            if tags:
                return " / ".join(tags)
            return None
            
        except Exception as e:
            logger.warning(f"Error getting playstyle match: {e}")
            return None
    
    async def save_champion_data(self, champion_data: dict) -> Optional[ChampionData]:
        """Save champion data to database"""
        # Not implemented for this repository
        return None
    
    async def get_player_champion_pool(self, puuid: str) -> List[str]:
        """Get player's champion pool using dynamic mastery distribution
        
        Uses a weighted scoring system based on mastery level and games played:
        - Higher mastery = higher weight
        - More games = higher weight
        - Includes champions above a dynamic percentile threshold
        
        Returns:
            List of graph champion names (e.g., ['Ahri', 'MonkeyKing', 'Syndra'])
        """
        try:
            # Query champion_progress table for this player's champions
            # Order by total_games to prioritize most played
            result = await self.db.table(DatabaseTable.CHAMPION_PROGRESS).select(
                'champion_id, champion_name, mastery_level, total_games, mastery_points'
            ).eq('puuid', puuid).order('total_games', desc=True).limit(200).execute()
            
            if not result.data:
                logger.warning(f"No champion progress found for puuid: {puuid}")
                return []
            
            # Calculate champion scores and determine dynamic threshold
            champion_pool = self._calculate_champion_pool_by_distribution(result.data)
            
            if champion_pool:
                logger.info(f"Champion pool (distribution-based): {len(champion_pool)} champions - {champion_pool}")
                return champion_pool
            
            # Fallback: if no mastery data, return top 5 by total_games
            logger.warning(f"No champions met distribution threshold, falling back to top by games")
            fallback_pool = []
            for champ in result.data[:5]:
                champion_id = champ.get('champion_id')
                if champion_id:
                    graph_name = get_graph_name_from_id(int(champion_id))
                    if graph_name:
                        fallback_pool.append(graph_name)
            
            logger.info(f"Champion pool (fallback): {fallback_pool}")
            return fallback_pool
            
        except Exception as e:
            logger.error(f"Error fetching player champion pool: {e}")
            return []
    
    def _calculate_champion_pool_by_distribution(self, champion_data: List[Dict]) -> List[str]:
        """Calculate champion pool using weighted scoring based on mastery distribution
        
        Scoring formula:
        - Mastery weight: mastery_level^2 (exponential - mastery 7 = 49x more than mastery 1)
        - Games weight: log(total_games + 1) (logarithmic - diminishing returns)
        - Points weight: log(mastery_points + 1) / 10 (minor boost)
        
        Threshold:
        - Include champions scoring above the 30th percentile
        - Ensures we capture "frequently played" champions
        - Adapts to player's overall distribution
        
        Args:
            champion_data: List of champion progress records
            
        Returns:
            List of graph champion names that meet the distribution threshold
        """
        if not champion_data:
            return []
        
        import math
        
        # Calculate score for each champion
        scored_champions = []
        for champ in champion_data:
            champion_id = champ.get('champion_id')
            mastery_level = champ.get('mastery_level') or 0
            total_games = champ.get('total_games') or 0
            mastery_points = champ.get('mastery_points') or 0
            
            if not champion_id or total_games == 0:
                continue
            
            # Weighted scoring formula
            mastery_weight = mastery_level ** 2  # Exponential: 1, 4, 9, 16, 25, 36, 49
            games_weight = math.log(total_games + 1)  # Logarithmic: diminishing returns
            points_weight = math.log(mastery_points + 1) / 10  # Minor boost
            
            # Combined score
            score = mastery_weight + games_weight + points_weight
            
            scored_champions.append({
                'champion_id': champion_id,
                'score': score,
                'mastery_level': mastery_level,
                'total_games': total_games
            })
        
        if not scored_champions:
            return []
        
        # Sort by score descending
        scored_champions.sort(key=lambda x: x['score'], reverse=True)
        
        # Calculate dynamic threshold based on score distribution
        scores = [c['score'] for c in scored_champions]
        
        # Adaptive percentile based on total champion count
        # - Very few champions (1-3): Include all
        # - Few champions (4-10): Use 10th percentile (top 90%)
        # - Medium champions (11-20): Use 20th percentile (top 80%)
        # - Many champions (21+): Use 30th percentile (top 70%)
        total_champs = len(scored_champions)
        
        if total_champs <= 3:
            # Include all champions for new players
            percentile_threshold = 0
            logger.info(f"New player detected ({total_champs} champions) - including all")
        elif total_champs <= 10:
            percentile_threshold = 10
            logger.info(f"Small pool detected ({total_champs} champions) - using 10th percentile")
        elif total_champs <= 20:
            percentile_threshold = 20
            logger.info(f"Medium pool detected ({total_champs} champions) - using 20th percentile")
        else:
            percentile_threshold = 30
            logger.info(f"Large pool detected ({total_champs} champions) - using 30th percentile")
        
        percentile_value = self._calculate_percentile(scores, percentile_threshold)
        
        # Include champions above threshold
        champion_pool = []
        included_count = 0
        for champ in scored_champions:
            if champ['score'] >= percentile_value:
                graph_name = get_graph_name_from_id(int(champ['champion_id']))
                if graph_name:
                    champion_pool.append(graph_name)
                    included_count += 1
        
        # Ensure minimum of 3 champions (for very edge cases)
        if included_count < 3 and total_champs >= 3:
            logger.warning(f"Only {included_count} champions included, adding top 3")
            champion_pool = []
            for champ in scored_champions[:3]:
                graph_name = get_graph_name_from_id(int(champ['champion_id']))
                if graph_name:
                    champion_pool.append(graph_name)
        
        logger.info(
            f"Distribution analysis: {total_champs} total champions, "
            f"{percentile_threshold}th percentile score = {percentile_value:.2f}, "
            f"included {len(champion_pool)} champions"
        )
        
        return champion_pool
    
    def _calculate_percentile(self, values: List[float], percentile: int) -> float:
        """Calculate the Nth percentile of a list of values
        
        Args:
            values: List of numeric values (should be sorted)
            percentile: Percentile to calculate (0-100)
            
        Returns:
            Value at the specified percentile
        """
        if not values:
            return 0.0
        
        sorted_values = sorted(values)
        index = (percentile / 100) * (len(sorted_values) - 1)
        
        # Linear interpolation between two nearest values
        lower_index = int(index)
        upper_index = min(lower_index + 1, len(sorted_values) - 1)
        weight = index - lower_index
        
        return sorted_values[lower_index] * (1 - weight) + sorted_values[upper_index] * weight
    
    async def get_player_champion_performance(self, puuid: str) -> Dict[str, Dict[str, float]]:
        """Get player's performance metrics (EPS/CPS) for their champion pool
        
        Returns:
            Dict mapping graph champion_name to performance metrics:
            {"Ahri": {"avg_eps": 75.5, "avg_cps": 82.3, "total_games": 45}, ...}
            {"MonkeyKing": {"avg_eps": 68.2, "avg_cps": 71.5, "total_games": 30}, ...}
        """
        try:
            result = await self.db.table(DatabaseTable.CHAMPION_PROGRESS).select(
                'champion_id, champion_name, avg_eps_score, avg_cps_score, total_games'
            ).eq('puuid', puuid).execute()
            
            if not result.data:
                return {}
            
            performance_map = {}
            for champ in result.data:
                champion_id = champ.get('champion_id')
                if champion_id:
                    # Convert champion ID to graph name to match champion pool
                    graph_name = get_graph_name_from_id(int(champion_id))
                    if graph_name:
                        performance_map[graph_name] = {
                            'avg_eps': champ.get('avg_eps_score', 0.0),
                            'avg_cps': champ.get('avg_cps_score', 0.0),
                            'total_games': champ.get('total_games', 0)
                        }
            
            return performance_map
            
        except Exception as e:
            logger.error(f"Error fetching player performance: {e}")
            return {}
