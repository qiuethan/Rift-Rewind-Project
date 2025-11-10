"""
Test script for ability similarities endpoint

This script tests the new GET /api/champions/{champion_id}/ability-similarities endpoint
to ensure it properly returns ability similarity data.
"""
import asyncio
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).resolve().parent))

from infrastructure.champion_repository import ChampionRepositoryImpl
from services.champion_service import ChampionService
from domain.champion_domain import ChampionDomain
from repositories.player_repository import PlayerRepository


class MockPlayerRepository(PlayerRepository):
    """Mock player repository for testing"""
    async def get_player_by_id(self, player_id: str):
        return None
    
    async def save_player(self, player_data: dict):
        return None
    
    async def get_player_summoner(self, player_id: str):
        return None
    
    async def get_summoner_by_puuid(self, puuid: str):
        return None
    
    async def get_summoner_by_riot_id(self, game_name: str, tag_line: str, region: str):
        return None
    
    async def get_summoner_by_name(self, summoner_name: str, region: str):
        return None
    
    async def save_summoner(self, summoner_data: dict):
        return None
    
    async def get_champion_masteries(self, puuid: str):
        return []
    
    async def get_champion_mastery_by_champion(self, puuid: str, champion_id: int):
        return None
    
    async def get_top_champion_masteries(self, puuid: str, limit: int = 10):
        return []
    
    async def get_match_history(self, puuid: str, region: str, count: int = 20):
        return []
    
    async def get_player_stats(self, puuid: str):
        return None
    
    async def get_mastery_score(self, puuid: str):
        return 0
    
    async def get_mastery_data(self, puuid: str, champion_id: int):
        return None
    
    async def get_ranked_data(self, summoner_id: str):
        return []
    
    async def get_user_summoner(self, user_id: str):
        return None
    
    async def get_user_summoner_basic(self, user_id: str):
        return None


async def test_ability_similarities():
    """Test the ability similarities functionality"""
    print("=" * 80)
    print("TESTING ABILITY SIMILARITIES ENDPOINT")
    print("=" * 80)
    print()
    
    # Initialize services
    print("1. Initializing services...")
    try:
        champion_repo = ChampionRepositoryImpl()
        player_repo = MockPlayerRepository()
        champion_domain = ChampionDomain()
        champion_service = ChampionService(
            champion_repository=champion_repo,
            player_repository=player_repo,
            champion_domain=champion_domain
        )
        print("   ✓ Services initialized successfully")
        print()
    except Exception as e:
        print(f"   ✗ Failed to initialize services: {e}")
        import traceback
        traceback.print_exc()
        return
    
    # Test champions
    test_champions = [
        "heimerdinger",
        "ahri",
        "yasuo",
        "lux",
        "zed"
    ]
    
    print("2. Testing ability similarities for various champions...")
    print()
    
    for champion_id in test_champions:
        print(f"Testing champion: {champion_id.upper()}")
        print("-" * 80)
        
        try:
            # Call service method
            response = await champion_service.get_ability_similarities(
                champion_id=champion_id,
                limit_per_ability=2  # Get top 2 for each ability
            )
            
            print(f"   Champion: {response.champion_name}")
            print(f"   Total similarities found: {len(response.abilities)}")
            print()
            
            # Group by ability type
            abilities_by_type = {}
            for ability in response.abilities:
                if ability.ability_type not in abilities_by_type:
                    abilities_by_type[ability.ability_type] = []
                abilities_by_type[ability.ability_type].append(ability)
            
            # Display results
            for ability_type in ['Q', 'W', 'E', 'R']:
                if ability_type in abilities_by_type:
                    abilities = abilities_by_type[ability_type]
                    print(f"   {ability_type} - {abilities[0].ability_name}:")
                    for ability in abilities:
                        print(f"      → Similar to {ability.similar_champion}'s {ability.similar_ability_type}")
                        print(f"        {ability.similar_ability_name}")
                        print(f"        Score: {ability.similarity_score:.2f}")
                        print(f"        Reason: {ability.explanation[:80]}...")
                        print()
            
            print(f"   ✓ Successfully retrieved ability similarities for {champion_id}")
            
        except Exception as e:
            print(f"   ✗ Failed for {champion_id}: {e}")
        
        print()
        print()
    
    print("=" * 80)
    print("TEST SUMMARY")
    print("=" * 80)
    print("All tests completed. Check results above for any failures.")
    print()


async def test_endpoint_error_cases():
    """Test error handling"""
    print("=" * 80)
    print("TESTING ERROR CASES")
    print("=" * 80)
    print()
    
    champion_repo = ChampionRepositoryImpl()
    player_repo = MockPlayerRepository()
    champion_domain = ChampionDomain()
    champion_service = ChampionService(
        champion_repository=champion_repo,
        player_repository=player_repo,
        champion_domain=champion_domain
    )
    
    # Test with non-existent champion
    print("1. Testing with non-existent champion...")
    try:
        response = await champion_service.get_ability_similarities(
            champion_id="nonexistentchampion",
            limit_per_ability=3
        )
        print(f"   Response: {response}")
    except Exception as e:
        print(f"   Expected error caught: {type(e).__name__} - {e}")
    print()
    
    # Test with invalid champion ID format
    print("2. Testing with empty champion ID...")
    try:
        response = await champion_service.get_ability_similarities(
            champion_id="",
            limit_per_ability=3
        )
        print(f"   Response: {response}")
    except Exception as e:
        print(f"   Expected error caught: {type(e).__name__} - {e}")
    print()


async def main():
    """Run all tests"""
    print("\n")
    print("╔" + "═" * 78 + "╗")
    print("║" + " " * 20 + "ABILITY SIMILARITIES API TEST" + " " * 29 + "║")
    print("╚" + "═" * 78 + "╝")
    print()
    
    # Test main functionality
    await test_ability_similarities()
    
    # Test error cases
    await test_endpoint_error_cases()
    
    print("=" * 80)
    print("ALL TESTS COMPLETED")
    print("=" * 80)
    print()


if __name__ == "__main__":
    asyncio.run(main())
