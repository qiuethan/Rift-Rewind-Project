"""
Match repository implementation with Riot API
"""
from repositories.match_repository import MatchRepository
from models.matches import MatchTimelineResponse, MatchSummaryResponse
from infrastructure.database.database_client import DatabaseClient
from typing import Optional, Dict, Any


class MatchRepositoryRiot(MatchRepository):
    """Riot API + Database implementation of match repository"""
    
    def __init__(self, client: DatabaseClient, riot_api_key: str):
        self.client = client
        self.riot_api_key = riot_api_key
    
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
            self.client.table('match_timelines').upsert(timeline_data).execute()
            return MatchTimelineResponse(**timeline_data)
        return None
    
    async def get_cached_timeline(self, match_id: str) -> Optional[MatchTimelineResponse]:
        """Get cached match timeline from database"""
        if self.client:
            response = self.client.table('match_timelines').select('*').eq('match_id', match_id).limit(1).execute()
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
