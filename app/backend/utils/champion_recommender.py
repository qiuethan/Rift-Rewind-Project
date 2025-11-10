"""
Champion recommendation system using graph-based collaborative filtering
and feature-based similarity.

Adapted from scripts/champion_recommender/train_model.py for production use.
"""
import json
import numpy as np
import pandas as pd
from collections import defaultdict, Counter
from pathlib import Path
from typing import List, Dict, Set, Tuple, Optional
from utils.logger import logger


class ChampionRecommender:
    """Champion recommendation engine using graph and feature embeddings"""
    
    def __init__(self, graph_data_path: str = None):
        """Initialize recommender with graph data
        
        Args:
            graph_data_path: Path to graph_data directory. If None, uses default location.
        """
        if graph_data_path is None:
            # Default to data/graph_data from project root
            graph_data_path = Path(__file__).resolve().parents[3] / 'data' / 'graph_data'
        else:
            graph_data_path = Path(graph_data_path)
        
        self.graph_data_path = graph_data_path
        self.graph: Dict[str, Dict[str, float]] = {}
        self.champ_node_data: Optional[pd.DataFrame] = None
        self.champ_to_id: Dict[str, int] = {}
        self.id_to_champ: Dict[int, str] = {}
        self.feat_embeddings: Optional[np.ndarray] = None
        
        self._load_graph_and_nodes()
    
    def _load_graph_and_nodes(self):
        """Load graph, node data, and mappings from files"""
        try:
            # Load champion graph (edge weights)
            graph_path = self.graph_data_path / "champion_graph.json"
            with open(graph_path, "r", encoding="utf-8") as f:
                self.graph = json.load(f)
            
            # Load champion node features
            node_data_path = self.graph_data_path / "champion_node_data.csv"
            self.champ_node_data = pd.read_csv(node_data_path)
            
            # Load champion mappings
            mappings_path = self.graph_data_path / "champion_mappings.json"
            with open(mappings_path, "r", encoding="utf-8") as f:
                mappings = json.load(f)
                self.champ_to_id = mappings["champ_to_id"]
                self.id_to_champ = {int(k): v for k, v in mappings["id_to_champ"].items()}
            
            # Create normalized feature embeddings
            self.feat_embeddings = np.array(
                self.champ_node_data.drop(columns=["championName", "index"]).values,
                dtype=np.float64
            )
            # L2 normalize
            self.feat_embeddings = self.feat_embeddings / (
                np.linalg.norm(self.feat_embeddings, axis=1, keepdims=True) + 1e-9
            )
            
            logger.info(f"Loaded champion graph with {len(self.champ_node_data)} champions")
            
        except Exception as e:
            logger.error(f"Error loading champion graph data: {e}")
            raise
    
    def _cosine_similarity(self, a: np.ndarray, b: np.ndarray) -> float:
        """Calculate cosine similarity between two vectors"""
        return np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b) + 1e-9)
    
    def _clean_recent_champions(
        self, 
        recent_champs: List[str], 
        max_occurrences: int = 5
    ) -> List[str]:
        """
        Filter out champions that appear too frequently in recent games.
        Returns list of champions to exclude from recommendations.
        
        Args:
            recent_champs: List of recently played champions
            max_occurrences: Maximum times a champion can appear before being excluded
            
        Returns:
            List of champion names to exclude
        """
        counts = Counter()
        to_remove = []
        for champ in recent_champs:
            counts[champ] += 1
            if counts[champ] > max_occurrences:
                to_remove.append(champ)
        return to_remove
    
    def _filter_champions(
        self, 
        filters: Optional[Dict[str, any]] = None
    ) -> Set[str]:
        """
        Filter champions based on feature constraints.
        
        Args:
            filters: Dict of feature constraints, e.g.:
                {"tag_Mage": 1, "difficulty": (">", 5)}
                
        Returns:
            Set of champion names that satisfy constraints
        """
        if filters is None or self.champ_node_data is None:
            return set(self.champ_node_data["championName"])
        
        filtered = self.champ_node_data.copy()
        
        for key, value in filters.items():
            if key.startswith("tag_"):
                # Categorical tag filter
                filtered = filtered[filtered[key] == value]
            elif isinstance(value, tuple):
                # Numeric comparison filter
                op, thresh = value
                if op == ">":
                    filtered = filtered[filtered[key] > thresh]
                elif op == "<":
                    filtered = filtered[filtered[key] < thresh]
                elif op == "==":
                    filtered = filtered[filtered[key] == thresh]
        
        return set(filtered["championName"])
    
    def _combined_similarity(
        self,
        champion_name: str,
        alpha: float = 0.7,
        allowed: Optional[Set[str]] = None
    ) -> Dict[str, float]:
        """
        Calculate combined similarity scores using graph and feature embeddings.
        
        Args:
            champion_name: Name of the champion to find similarities for
            alpha: Weight for graph similarity (0-1). (1-alpha) is feature weight.
            allowed: Set of allowed champion names to consider
            
        Returns:
            Dict mapping champion names to similarity scores
        """
        if champion_name not in self.champ_to_id:
            logger.warning(f"Champion '{champion_name}' not found in mappings")
            return {}
        
        champ_id = self.champ_to_id[champion_name]
        
        # Graph-based similarity (edge weights from co-play patterns)
        graph_sims = {
            b: w 
            for b, w in self.graph.get(champion_name, {}).items() 
            if allowed is None or b in allowed
        }
        
        # Feature-based similarity (cosine similarity of stats/tags)
        feats = self.feat_embeddings[champ_id]
        cos_sims = {}
        for i, other in self.id_to_champ.items():
            if allowed and other not in allowed:
                continue
            cos_sims[other] = self._cosine_similarity(feats, self.feat_embeddings[i])
        
        # Combine: weighted sum of graph and feature similarities
        combined = {}
        all_champs = set(list(graph_sims.keys()) + list(cos_sims.keys()))
        
        for champ in all_champs:
            g = graph_sims.get(champ, 0)
            f = cos_sims.get(champ, 0)
            combined[champ] = alpha * g + (1 - alpha) * f
        
        return combined
    
    def recommend_from_champion_pool(
        self,
        champion_list: List[str],
        top_k: int = 5,
        alpha: float = 0.7,
        filters: Optional[Dict[str, any]] = None,
        max_occurrences: int = 2
    ) -> List[Tuple[str, float]]:
        """
        Recommend champions based on a list of played champions.
        
        Args:
            champion_list: List of champion names (player's champion pool)
            top_k: Number of recommendations to return
            alpha: Weight for graph similarity (0-1)
            filters: Optional feature constraints for filtering
            max_occurrences: Max times a champion can appear in pool before exclusion
            
        Returns:
            List of (champion_name, score) tuples, sorted by score descending
        """
        if not champion_list:
            logger.warning("Empty champion list provided for recommendations")
            return []
        
        # Get allowed champions based on filters
        allowed = self._filter_champions(filters)
        
        # Aggregate similarity scores across all champions in the pool
        combined_scores = defaultdict(float)
        
        for champ in champion_list:
            if champ not in self.champ_to_id:
                logger.warning(f"Champion '{champ}' not in graph, skipping")
                continue
            
            # Get similarities for this champion
            recs = self._combined_similarity(champ, alpha=alpha, allowed=allowed)
            
            # Add to aggregate scores
            for r, score in recs.items():
                combined_scores[r] += score
        
        # Sort by aggregated score
        sorted_recs = sorted(combined_scores.items(), key=lambda x: x[1], reverse=True)
        
        # Exclude champions that appear too frequently in the pool
        to_remove = self._clean_recent_champions(champion_list, max_occurrences=max_occurrences)
        
        # Filter out excluded champions and return top_k
        filtered_recs = [
            (c, score) 
            for c, score in sorted_recs 
            if c not in to_remove
        ]
        
        return filtered_recs[:top_k]


# Singleton instance for reuse across requests
_recommender_instance: Optional[ChampionRecommender] = None


def get_recommender() -> ChampionRecommender:
    """Get or create singleton ChampionRecommender instance"""
    global _recommender_instance
    if _recommender_instance is None:
        _recommender_instance = ChampionRecommender()
    return _recommender_instance
