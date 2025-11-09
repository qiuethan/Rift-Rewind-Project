"""
Test script for routing with headers (simulating frontend requests)
Tests how the backend handles requests with puuid, champion, match_id in headers
"""
import asyncio
import sys
from pathlib import Path
from typing import Optional

# Add backend to path
sys.path.insert(0, str(Path(__file__).parent))

from infrastructure.bedrock_repository import BedrockRepository
from infrastructure.context_repository import ContextRepositorySupabase
from infrastructure.database.database_client import DatabaseClient
from services.llm_service import LLMService
from config.settings import settings


class FrontendRequestSimulator:
    """Simulates frontend requests with headers"""
    
    def __init__(self, llm_service: LLMService):
        self.llm_service = llm_service
    
    async def simulate_request(
        self,
        prompt: str,
        puuid: str,
        champion_name: Optional[str] = None,
        match_id: Optional[str] = None,
        page_context: Optional[str] = None
    ):
        """
        Simulate a frontend request with headers
        
        Args:
            prompt: User's question/prompt
            puuid: Player UUID (from header)
            champion_name: Optional champion name (from header, for champion-specific pages)
            match_id: Optional match ID (from header, for match detail pages)
            page_context: Optional page context (e.g., "dashboard", "champion_detail", "match_detail")
        """
        print("\n" + "=" * 80)
        print("SIMULATING FRONTEND REQUEST")
        print("=" * 80)
        print(f"📝 Prompt: \"{prompt}\"")
        print(f"👤 PUUID: {puuid}")
        if champion_name:
            print(f"🎮 Champion: {champion_name}")
        if match_id:
            print(f"🎯 Match ID: {match_id}")
        if page_context:
            print(f"📄 Page Context: {page_context}")
        print("-" * 80)
        
        try:
            # Call the smart routing service
            result = await self.llm_service.generate_with_smart_routing(
                puuid=puuid,
                prompt=prompt,
                match_id=match_id
            )
            
            print("\n✅ RESPONSE GENERATED")
            print("-" * 80)
            print(f"🤖 Model Used: {result['model_used']}")
            print(f"📊 Complexity: {result['complexity']}")
            print(f"🗂️  Contexts Used: {', '.join(result['contexts_used'])}")
            print(f"\n💬 Response:\n{result['text']}")
            print("-" * 80)
            
            # Show what data was fetched
            if 'contexts_data' in result:
                print("\n📦 FETCHED DATA:")
                for ctx_name, ctx_data in result['contexts_data'].items():
                    print(f"  - {ctx_name}: {list(ctx_data.keys())}")
            
            return result
            
        except Exception as e:
            print(f"\n❌ ERROR: {e}")
            import traceback
            traceback.print_exc()
            return None


async def test_dashboard_page():
    """Test: User on dashboard page asking general questions"""
    print("\n" + "🏠" * 40)
    print("TEST SCENARIO: Dashboard Page")
    print("🏠" * 40)
    print("Context: User is on their dashboard, no specific champion or match selected")
    
    if not settings.SUPABASE_URL or not settings.SUPABASE_KEY:
        print("⚠️  Skipping - no database credentials")
        return
    
    # Setup
    db = DatabaseClient(settings.SUPABASE_URL, settings.SUPABASE_KEY)
    bedrock_repo = BedrockRepository()
    context_repo = ContextRepositorySupabase(db)
    llm_service = LLMService(bedrock_repo, context_repo)
    simulator = FrontendRequestSimulator(llm_service)
    
    # Get a test PUUID from user
    print("\n📋 You need a valid PUUID from your database to test.")
    puuid = input("Enter PUUID (or press Enter to skip): ").strip()
    
    if not puuid:
        print("⏭️  Skipped")
        return
    
    # Test cases for dashboard
    test_prompts = [
        "How am I doing overall?",
        "What champions should I focus on?",
        "Give me some tips to improve"
    ]
    
    for prompt in test_prompts:
        await simulator.simulate_request(
            prompt=prompt,
            puuid=puuid,
            page_context="dashboard"
        )
        await asyncio.sleep(1)  # Rate limiting


async def test_champion_detail_page():
    """Test: User on champion detail page"""
    print("\n" + "🎮" * 40)
    print("TEST SCENARIO: Champion Detail Page")
    print("🎮" * 40)
    print("Context: User is viewing their stats for a specific champion (e.g., Yasuo)")
    
    if not settings.SUPABASE_URL or not settings.SUPABASE_KEY:
        print("⚠️  Skipping - no database credentials")
        return
    
    # Setup
    db = DatabaseClient(settings.SUPABASE_URL, settings.SUPABASE_KEY)
    bedrock_repo = BedrockRepository()
    context_repo = ContextRepositorySupabase(db)
    llm_service = LLMService(bedrock_repo, context_repo)
    simulator = FrontendRequestSimulator(llm_service)
    
    # Get test data from user
    print("\n📋 You need a valid PUUID and champion name from your database.")
    puuid = input("Enter PUUID (or press Enter to skip): ").strip()
    
    if not puuid:
        print("⏭️  Skipped")
        return
    
    champion = input("Enter champion name (e.g., Yasuo, Ahri): ").strip()
    
    # Test cases for champion detail page
    test_prompts = [
        f"How am I doing on {champion}?",
        f"What should I improve on {champion}?",
        f"Am I getting better at {champion}?",
        "Give me tips for this champion"  # Frontend should include champion in header
    ]
    
    for prompt in test_prompts:
        await simulator.simulate_request(
            prompt=prompt,
            puuid=puuid,
            champion_name=champion,
            page_context="champion_detail"
        )
        await asyncio.sleep(1)


async def test_match_detail_page():
    """Test: User on match detail page"""
    print("\n" + "🎯" * 40)
    print("TEST SCENARIO: Match Detail Page")
    print("🎯" * 40)
    print("Context: User is viewing a specific match")
    
    if not settings.SUPABASE_URL or not settings.SUPABASE_KEY:
        print("⚠️  Skipping - no database credentials")
        return
    
    # Setup
    db = DatabaseClient(settings.SUPABASE_URL, settings.SUPABASE_KEY)
    bedrock_repo = BedrockRepository()
    context_repo = ContextRepositorySupabase(db)
    llm_service = LLMService(bedrock_repo, context_repo)
    simulator = FrontendRequestSimulator(llm_service)
    
    # Get test data from user
    print("\n📋 You need a valid PUUID and match_id from your database.")
    puuid = input("Enter PUUID (or press Enter to skip): ").strip()
    
    if not puuid:
        print("⏭️  Skipped")
        return
    
    match_id = input("Enter match_id (e.g., NA1_1234567890): ").strip()
    
    # Test cases for match detail page
    test_prompts = [
        "How did I do in this game?",
        "What went wrong in this match?",
        "What should I have done differently?",
        "Analyze my performance"
    ]
    
    for prompt in test_prompts:
        await simulator.simulate_request(
            prompt=prompt,
            puuid=puuid,
            match_id=match_id,
            page_context="match_detail"
        )
        await asyncio.sleep(1)


async def test_custom_scenario():
    """Test: Custom scenario with user input"""
    print("\n" + "🔧" * 40)
    print("TEST SCENARIO: Custom Test")
    print("🔧" * 40)
    
    if not settings.SUPABASE_URL or not settings.SUPABASE_KEY:
        print("⚠️  Skipping - no database credentials")
        return
    
    # Setup
    db = DatabaseClient(settings.SUPABASE_URL, settings.SUPABASE_KEY)
    bedrock_repo = BedrockRepository()
    context_repo = ContextRepositorySupabase(db)
    llm_service = LLMService(bedrock_repo, context_repo)
    simulator = FrontendRequestSimulator(llm_service)
    
    # Get test data from user
    print("\n📋 Enter your test parameters:")
    puuid = input("PUUID: ").strip()
    
    if not puuid:
        print("⏭️  Skipped")
        return
    
    prompt = input("Prompt: ").strip()
    champion = input("Champion (optional, press Enter to skip): ").strip() or None
    match_id = input("Match ID (optional, press Enter to skip): ").strip() or None
    
    await simulator.simulate_request(
        prompt=prompt,
        puuid=puuid,
        champion_name=champion,
        match_id=match_id,
        page_context="custom"
    )


def print_integration_guide():
    """Print guide for frontend integration"""
    print("\n" + "=" * 80)
    print("FRONTEND INTEGRATION GUIDE")
    print("=" * 80)
    print("""
The frontend should include these headers in API requests to the LLM endpoint:

1. **Authentication Header** (required):
   Authorization: Bearer <jwt_token>
   
2. **Context Headers** (based on current page):
   
   a) Dashboard Page:
      - Just send the prompt
      - Backend will use PUUID from auth token
   
   b) Champion Detail Page:
      - Include champion info in the request body or as query param
      - Example: { "prompt": "...", "champion_id": 157 }
   
   c) Match Detail Page:
      - Include match_id in the request body
      - Example: { "prompt": "...", "match_id": "NA1_1234567890" }

RECOMMENDED API ENDPOINT STRUCTURE:
POST /api/llm/chat
Headers:
  Authorization: Bearer <token>
Body:
  {
    "prompt": "How am I doing on Yasuo?",
    "match_id": "NA1_1234567890",  // Optional
    "champion_id": 157,             // Optional
    "page_context": "champion_detail"  // Optional, for analytics
  }

The backend will:
1. Extract PUUID from the JWT token
2. Use smart routing to determine what data to fetch
3. Automatically fetch summoner, champion progress, or match data as needed
4. Return AI-generated response with appropriate context
""")
    print("=" * 80)


def main():
    """Main test runner"""
    print("\n🚀 Starting Routing Tests with Headers...\n")
    
    # Show integration guide first
    print_integration_guide()
    
    print("\n" + "=" * 80)
    print("SELECT TEST SCENARIO")
    print("=" * 80)
    print("1. Dashboard Page (general questions)")
    print("2. Champion Detail Page (champion-specific questions)")
    print("3. Match Detail Page (match-specific questions)")
    print("4. Custom Test (your own parameters)")
    print("5. Run All Tests")
    print("=" * 80)
    
    choice = input("\nEnter choice (1-5): ").strip()
    
    if choice == "1":
        asyncio.run(test_dashboard_page())
    elif choice == "2":
        asyncio.run(test_champion_detail_page())
    elif choice == "3":
        asyncio.run(test_match_detail_page())
    elif choice == "4":
        asyncio.run(test_custom_scenario())
    elif choice == "5":
        async def run_all():
            await test_dashboard_page()
            await test_champion_detail_page()
            await test_match_detail_page()
        asyncio.run(run_all())
    else:
        print("Invalid choice")
        return
    
    print("\n" + "=" * 80)
    print("✅ Tests Complete!")
    print("=" * 80)


if __name__ == "__main__":
    main()
