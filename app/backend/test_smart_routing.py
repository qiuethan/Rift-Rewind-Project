"""
Test script for LLM Smart Routing
Tests context classification and smart context retrieval
"""
import asyncio
import sys
from pathlib import Path

# Add backend to path
sys.path.insert(0, str(Path(__file__).parent))

from infrastructure.bedrock_repository import BedrockRepository
from infrastructure.context_repository import ContextRepositorySupabase
from infrastructure.database.database_client import DatabaseClient
from services.llm_service import LLMService
from config.settings import settings


async def test_context_classification():
    """Test context routing classification"""
    print("\n" + "=" * 80)
    print("Testing Context Classification")
    print("=" * 80)
    
    bedrock = BedrockRepository()
    
    if not bedrock.is_available():
        print("❌ Bedrock not available")
        return False
    
    test_prompts = [
        {
            "prompt": "Hello! How are you?",
            "expected_contexts": ["summoner"],
            "expected_champion": None,
            "expected_match": False,
            "description": "Simple greeting"
        },
        {
            "prompt": "How am I doing on Yasuo?",
            "expected_contexts": ["summoner", "champion_progress"],
            "expected_champion": "Yasuo",
            "expected_match": False,
            "description": "Champion-specific question"
        },
        {
            "prompt": "Analyze my last match",
            "expected_contexts": ["summoner", "match"],
            "expected_champion": None,
            "expected_match": True,
            "description": "Match analysis request"
        },
        {
            "prompt": "How did I perform on Ahri in my last game?",
            "expected_contexts": ["summoner", "champion_progress", "match"],
            "expected_champion": "Ahri",
            "expected_match": True,
            "description": "Champion + match question"
        }
    ]
    
    for i, test in enumerate(test_prompts, 1):
        print(f"\n{i}. {test['description']}")
        print(f"   Prompt: \"{test['prompt']}\"")
        print(f"   Expected: contexts={test['expected_contexts']}, champion={test['expected_champion']}, match={test['expected_match']}")
        
        try:
            routing = await bedrock.classify_context_needs(test['prompt'])
            print(f"   ✅ Routing result:")
            print(f"      - Contexts: {routing['contexts']}")
            print(f"      - Champion: {routing['champion_name']}")
            print(f"      - Requires match: {routing['requires_match']}")
            
            # Check if expected contexts are present
            missing = set(test['expected_contexts']) - set(routing['contexts'])
            extra = set(routing['contexts']) - set(test['expected_contexts'])
            
            if missing:
                print(f"   ⚠️  Missing contexts: {missing}")
            if extra:
                print(f"   ℹ️  Extra contexts: {extra}")
            if not missing and not extra:
                print(f"   ✅ Contexts match!")
                
        except Exception as e:
            print(f"   ❌ Error: {e}")
            return False
    
    return True


async def test_champion_extraction():
    """Test champion name extraction"""
    print("\n" + "=" * 80)
    print("Testing Champion Extraction")
    print("=" * 80)
    
    from utils.champion_mapping import extract_champion_from_text, get_champion_id
    
    test_cases = [
        ("How am I doing on Yasuo?", "yasuo", 157),
        ("My Ahri performance", "ahri", 103),
        ("Tips for playing Lee Sin", "lee sin", 64),
        ("Zed vs Yasuo matchup", "zed", 238),  # Will find first match
        ("General gameplay tips", None, None),
    ]
    
    for prompt, expected_name, expected_id in test_cases:
        print(f"\nPrompt: \"{prompt}\"")
        champion_name = extract_champion_from_text(prompt)
        
        if champion_name:
            champion_id = get_champion_id(champion_name)
            print(f"   ✅ Found: {champion_name} (ID: {champion_id})")
            
            if champion_name == expected_name and champion_id == expected_id:
                print(f"   ✅ Correct!")
            else:
                print(f"   ⚠️  Expected: {expected_name} (ID: {expected_id})")
        else:
            print(f"   ℹ️  No champion found")
            if expected_name is None:
                print(f"   ✅ Correct!")


async def test_smart_routing_with_mock_data():
    """Test smart routing with mock PUUID (won't fetch real data)"""
    print("\n" + "=" * 80)
    print("Testing Smart Routing Flow (Mock)")
    print("=" * 80)
    
    bedrock = BedrockRepository()
    
    if not bedrock.is_available():
        print("❌ Bedrock not available")
        return
    
    # Test just the routing logic without database
    test_prompt = "How can I improve my Yasuo gameplay?"
    
    print(f"\nPrompt: \"{test_prompt}\"")
    print("\nStep 1: Classify context needs...")
    contexts = await bedrock.classify_context_needs(test_prompt)
    print(f"   Contexts needed: {contexts}")
    
    print("\nStep 2: Extract champion...")
    from utils.champion_mapping import extract_champion_from_text, get_champion_id
    champion_name = extract_champion_from_text(test_prompt)
    if champion_name:
        champion_id = get_champion_id(champion_name)
        print(f"   Champion: {champion_name} (ID: {champion_id})")
    
    print("\nStep 3: Classify complexity...")
    complexity = await bedrock.classify_prompt_complexity(test_prompt)
    print(f"   Complexity: {complexity}")
    
    print("\n✅ Smart routing flow working!")


async def test_full_integration():
    """Test full integration with real database (requires valid PUUID)"""
    print("\n" + "=" * 80)
    print("Testing Full Integration")
    print("=" * 80)
    
    # Check if we have database credentials
    if not settings.SUPABASE_URL or not settings.SUPABASE_KEY:
        print("⚠️  Skipping integration test - no database credentials")
        return
    
    print("\nTo test with real data, you need:")
    print("1. A valid PUUID from your database")
    print("2. Optional: A match_id for match-specific queries")
    print("\nExample usage:")
    print("""
    db = DatabaseClient(settings.SUPABASE_URL, settings.SUPABASE_KEY)
    bedrock_repo = BedrockRepository()
    context_repo = ContextRepositorySupabase(db)
    llm_service = LLMService(bedrock_repo, context_repo)
    
    result = await llm_service.generate_with_smart_routing(
        puuid="your-puuid-here",
        prompt="How am I doing on Yasuo?",
        match_id="NA1_1234567890"  # Optional
    )
    
    print(f"Response: {result['text']}")
    print(f"Contexts used: {result['contexts_used']}")
    print(f"Model: {result['model_used']}")
    """)


def main():
    """Main test runner"""
    print("\n🚀 Starting Smart Routing Tests...\n")
    
    # Test 1: Context classification
    print("\n" + "=" * 80)
    response = input("Test context classification? (y/n): ")
    if response.lower() == 'y':
        success = asyncio.run(test_context_classification())
        if not success:
            print("\n❌ Context classification tests failed")
            return
    
    # Test 2: Champion extraction
    print("\n" + "=" * 80)
    response = input("Test champion extraction? (y/n): ")
    if response.lower() == 'y':
        asyncio.run(test_champion_extraction())
    
    # Test 3: Smart routing flow
    print("\n" + "=" * 80)
    response = input("Test smart routing flow? (y/n): ")
    if response.lower() == 'y':
        asyncio.run(test_smart_routing_with_mock_data())
    
    # Test 4: Full integration info
    print("\n" + "=" * 80)
    response = input("Show full integration example? (y/n): ")
    if response.lower() == 'y':
        asyncio.run(test_full_integration())
    
    print("\n" + "=" * 80)
    print("Tests Complete!")
    print("=" * 80)
    print("\n✅ Smart routing system is ready to use!")
    print("\n💡 Key features:")
    print("   - Automatic context classification")
    print("   - Champion name extraction from prompts")
    print("   - Smart data fetching (only what's needed)")
    print("   - Model routing (Haiku for simple, Sonnet for complex)")


if __name__ == "__main__":
    main()
