"""
Test script for AWS Bedrock integration
Run this to verify your Bedrock setup is working correctly
"""
import asyncio
import sys
from pathlib import Path

# Add backend to path
sys.path.insert(0, str(Path(__file__).parent))

from infrastructure.bedrock_repository import BedrockRepository
from config.settings import settings

async def test_bedrock():
    """Test Bedrock connection and basic functionality"""
    print("=" * 60)
    print("AWS Bedrock Connection Test")
    print("=" * 60)
    
    # Check environment variables
    print("\n1. Checking environment variables...")
    if not settings.AWS_ACCESS_KEY_ID:
        print("   ❌ AWS_ACCESS_KEY_ID not set")
        return False
    else:
        print(f"   ✅ AWS_ACCESS_KEY_ID: {settings.AWS_ACCESS_KEY_ID[:8]}...")
    
    if not settings.AWS_SECRET_ACCESS_KEY:
        print("   ❌ AWS_SECRET_ACCESS_KEY not set")
        return False
    else:
        print(f"   ✅ AWS_SECRET_ACCESS_KEY: {'*' * 20}")
    
    print(f"   ✅ AWS_REGION: {settings.AWS_REGION}")
    print(f"   ✅ AWS_BEDROCK_MODEL: {settings.AWS_BEDROCK_MODEL}")
    
    # Initialize Bedrock
    print("\n2. Initializing Bedrock client...")
    bedrock = BedrockRepository()
    
    if not bedrock.is_available():
        print("   ❌ Bedrock client not initialized")
        print("   Check your AWS credentials and try again")
        return False
    
    print("   ✅ Bedrock client initialized successfully!")
    
    # Test generation
    print("\n3. Testing text generation...")
    try:
        test_prompt = "Say 'Hello from AWS Bedrock!' in a friendly, enthusiastic way."
        print(f"   Prompt: {test_prompt}")
        print("   Waiting for response...")
        
        response = await bedrock.generate_text(test_prompt)
        
        print(f"\n   📝 Response from Claude:")
        print(f"   {'-' * 56}")
        print(f"   {response}")
        print(f"   {'-' * 56}")
        
        print("\n✅ Bedrock is working correctly!")
        return True
        
    except Exception as e:
        print(f"\n   ❌ Error during generation: {e}")
        print(f"   Error type: {type(e).__name__}")
        
        # Provide specific troubleshooting
        error_str = str(e).lower()
        if "credentials" in error_str or "access" in error_str:
            print("\n   💡 Troubleshooting:")
            print("   - Verify your AWS credentials are correct")
            print("   - Check IAM user has AmazonBedrockFullAccess policy")
        elif "model" in error_str:
            print("\n   💡 Troubleshooting:")
            print("   - Request model access in AWS Bedrock console")
            print("   - Verify model ID is correct")
        elif "region" in error_str:
            print("\n   💡 Troubleshooting:")
            print("   - Check AWS_REGION in .env file")
            print("   - Verify Bedrock is available in your region")
        
        return False

async def test_prompt_routing():
    """Test prompt routing with different complexity levels"""
    print("\n" + "=" * 60)
    print("Testing Prompt Routing")
    print("=" * 60)
    
    bedrock = BedrockRepository()
    
    if not bedrock.is_available():
        print("❌ Bedrock not available")
        return
    
    test_cases = [
        {
            "prompt": "Hello!",
            "expected": "simple",
            "description": "Simple greeting"
        },
        {
            "prompt": "What is KDA?",
            "expected": "simple",
            "description": "Basic question"
        },
        {
            "prompt": "Analyze this match: I played Yasuo mid and went 10/3/5. We won but I felt like I could have roamed more. What should I improve?",
            "expected": "moderate",
            "description": "Match analysis"
        },
        {
            "prompt": "Given the current meta, predict the optimal team composition for countering a poke-heavy comp with Xerath, Caitlyn, and Karma. Consider draft phase, win conditions, and macro strategy.",
            "expected": "complex",
            "description": "Strategic analysis"
        }
    ]
    
    for i, test in enumerate(test_cases, 1):
        print(f"\n{i}. {test['description']}")
        print(f"   Prompt: {test['prompt'][:80]}{'...' if len(test['prompt']) > 80 else ''}")
        print(f"   Expected complexity: {test['expected']}")
        
        try:
            result = await bedrock.generate_text_with_routing(test['prompt'])
            
            print(f"   ✅ Classified as: {result['complexity']}")
            print(f"   📦 Model used: {result['model_used'].split('.')[-1]}")
            print(f"   📝 Response: {result['text'][:150]}{'...' if len(result['text']) > 150 else ''}")
            
            if result['complexity'] == test['expected']:
                print(f"   ✅ Routing correct!")
            else:
                print(f"   ⚠️  Expected {test['expected']}, got {result['complexity']}")
                
        except Exception as e:
            print(f"   ❌ Error: {e}")

async def test_use_case_routing():
    """Test predefined use case routing"""
    print("\n" + "=" * 60)
    print("Testing Use Case Routing")
    print("=" * 60)
    
    bedrock = BedrockRepository()
    
    if not bedrock.is_available():
        print("❌ Bedrock not available")
        return
    
    use_cases = [
        ("greeting", "Hi there!"),
        ("match_summary", "Summarize my last game"),
        ("team_comp_analysis", "Analyze our team comp")
    ]
    
    for use_case, prompt in use_cases:
        print(f"\n📋 Use case: {use_case}")
        print(f"   Prompt: {prompt}")
        
        try:
            result = await bedrock.generate_text_with_routing(prompt, use_case=use_case)
            print(f"   ✅ Routed to: {result['model_used'].split('.')[-1]}")
            print(f"   📝 Response: {result['text'][:100]}{'...' if len(result['text']) > 100 else ''}")
        except Exception as e:
            print(f"   ❌ Error: {e}")

def main():
    """Main test runner"""
    print("\n🚀 Starting AWS Bedrock tests...\n")
    
    # Run basic test
    success = asyncio.run(test_bedrock())
    
    if success:
        # Run routing tests
        print("\n\n" + "=" * 60)
        response = input("Test prompt routing? (y/n): ")
        if response.lower() == 'y':
            asyncio.run(test_prompt_routing())
        
        print("\n\n" + "=" * 60)
        response = input("Test use case routing? (y/n): ")
        if response.lower() == 'y':
            asyncio.run(test_use_case_routing())
    
    print("\n" + "=" * 60)
    print("Test Complete")
    print("=" * 60)
    
    if success:
        print("✅ All tests passed! Bedrock prompt router is ready to use.")
        print("\n💡 The router automatically selects:")
        print("   - Haiku 4.5 (fast & cheap) for simple queries")
        print("   - Sonnet 4.5 for moderate and complex tasks")
    else:
        print("❌ Tests failed. Check the errors above and refer to BEDROCK_SETUP.md")

if __name__ == "__main__":
    main()
