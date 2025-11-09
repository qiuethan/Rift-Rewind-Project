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

async def test_multiple_prompts():
    """Test multiple prompts to verify consistency"""
    print("\n" + "=" * 60)
    print("Testing Multiple Prompts")
    print("=" * 60)
    
    bedrock = BedrockRepository()
    
    if not bedrock.is_available():
        print("❌ Bedrock not available")
        return
    
    prompts = [
        "What is League of Legends in one sentence?",
        "Name 3 popular League of Legends champions.",
        "What does KDA stand for in gaming?"
    ]
    
    for i, prompt in enumerate(prompts, 1):
        print(f"\n{i}. Prompt: {prompt}")
        try:
            response = await bedrock.generate_text(prompt)
            print(f"   Response: {response[:100]}{'...' if len(response) > 100 else ''}")
        except Exception as e:
            print(f"   ❌ Error: {e}")

def main():
    """Main test runner"""
    print("\n🚀 Starting AWS Bedrock tests...\n")
    
    # Run basic test
    success = asyncio.run(test_bedrock())
    
    if success:
        # Run additional tests
        response = input("\n\nRun additional tests? (y/n): ")
        if response.lower() == 'y':
            asyncio.run(test_multiple_prompts())
    
    print("\n" + "=" * 60)
    print("Test Complete")
    print("=" * 60)
    
    if success:
        print("✅ All tests passed! Bedrock is ready to use.")
    else:
        print("❌ Tests failed. Check the errors above and refer to BEDROCK_SETUP.md")

if __name__ == "__main__":
    main()
