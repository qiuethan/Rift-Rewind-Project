"""
Player repository implementation with Riot API and Firebase
"""
from repositories.player_repository import PlayerRepository
from models.players import SummonerResponse, PlayerStatsResponse
from fastapi import HTTPException, status
from typing import Optional, List


class PlayerRepositoryRiot(PlayerRepository):
    """Riot API + Supabase implementation of player repository"""
    
    def __init__(self, client, riot_api_key: str):
        self.client = client
        self.riot_api_key = riot_api_key
    
    async def get_summoner_by_name(self, summoner_name: str, region: str) -> Optional[SummonerResponse]:
        """Get summoner data by name from Riot API (DEMO)"""
        # Demo implementation - would call Riot API
        return SummonerResponse(
            id=f"demo_summoner_{summoner_name}",
            summoner_name=summoner_name,
            region=region,
            puuid=f"demo_puuid_{summoner_name}",
            summoner_level=100,
            profile_icon_id=1,
            last_updated="2024-01-01T00:00:00Z"
        )
    
    async def get_summoner_by_puuid(self, puuid: str) -> Optional[SummonerResponse]:
        """Get summoner data by PUUID from Riot API (DEMO)"""
        # Demo implementation
        return SummonerResponse(
            id=f"demo_summoner_id",
            summoner_name="DemoSummoner",
            region="NA1",
            puuid=puuid,
            summoner_level=100,
            profile_icon_id=1,
            last_updated="2024-01-01T00:00:00Z"
        )
    
    async def save_summoner(self, user_id: str, summoner_data: dict) -> SummonerResponse:
        """Save summoner data to Supabase"""
        try:
            if self.client:
                summoner_data['user_id'] = user_id
                self.client.table('summoners').upsert(summoner_data).execute()
            return SummonerResponse(**summoner_data)
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to save summoner: {str(e)}"
            )
    
    async def get_user_summoner(self, user_id: str) -> Optional[SummonerResponse]:
        """Get user's linked summoner from Supabase"""
        try:
            if self.client:
                response = self.client.table('summoners').select('*').eq('user_id', user_id).limit(1).execute()
                if response.data:
                    return SummonerResponse(**response.data[0])
            return None
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to get summoner: {str(e)}"
            )
    
    async def get_player_stats(self, summoner_id: str) -> Optional[PlayerStatsResponse]:
        """Get player statistics (DEMO)"""
        # Demo implementation
        return PlayerStatsResponse(
            summoner_id=summoner_id,
            total_games=100,
            wins=55,
            losses=45,
            win_rate=55.0,
            favorite_champions=["Ahri", "Lux", "Syndra"],
            average_kda=3.2,
            average_cs_per_min=7.5
        )
    
    async def get_match_history(self, puuid: str, count: int) -> List[str]:
        """Get match history for a player (DEMO)"""
        # Demo implementation
        return [f"NA1_demo_match_{i}" for i in range(count)]
