# AWS Bedrock Setup Guide

This guide will help you set up AWS Bedrock (Claude 3.5 Sonnet) for the Rift Rewind backend.

## Prerequisites

- AWS Account with Bedrock access
- Python virtual environment activated
- Backend dependencies installed (`pip install -r requirements.txt`)

## Step 1: Enable Bedrock Model Access

1. **Log in to AWS Console**: https://console.aws.amazon.com/
2. **Navigate to Bedrock**: Search for "Bedrock" in the services search bar
3. **Submit Anthropic Use Case Form** (REQUIRED - One-time only):
   - Go to "Model access" in the left sidebar
   - Click "Manage model access" or "Request model access"
   - Find any **Anthropic Claude** model
   - Click "Request model access" or "Edit" if already requested
   - You'll see a form asking about your use case
   - Fill out the form with:
     - **Use case**: "AI-powered gaming analytics and match analysis for League of Legends"
     - **Company/Organization**: Your name or company
     - **Industry**: Gaming/Entertainment
     - **Intended use**: "Analyzing game matches, providing player insights, and generating strategic recommendations"
   - Submit the form
   - **Wait 15-30 minutes** for approval (usually automatic)

4. **Request Model Access**:
   - After the form is approved, go back to "Model access"
   - Find and enable these models:
     - **Claude Haiku 4.5** (`anthropic.claude-haiku-4-5-20251001-v1:0`)
     - **Claude Sonnet 4.5** (`anthropic.claude-sonnet-4-5-20250929-v1:0`)
   - Check the boxes next to them
   - Click "Save changes" or "Request model access"
   - Wait for approval (usually instant after use case form is approved)

## Step 2: Create IAM User for Bedrock

1. **Navigate to IAM**: https://console.aws.amazon.com/iam/
2. **Create New User**:
   - Click "Users" → "Create user"
   - Username: `rift-rewind-bedrock` (or your preferred name)
   - Click "Next"

3. **Set Permissions**:
   - Select "Attach policies directly"
   - Search for and attach: `AmazonBedrockFullAccess`
   - Click "Next" → "Create user"

4. **Create Access Keys**:
   - Click on the newly created user
   - Go to "Security credentials" tab
   - Scroll to "Access keys" section
   - Click "Create access key"
   - Select "Application running outside AWS"
   - Click "Next" → "Create access key"
   - **IMPORTANT**: Copy both the Access Key ID and Secret Access Key
   - Store them securely (you won't be able to see the secret again!)

## Step 3: Configure Environment Variables

Add the following to your `.env` file in the backend directory:

```env
# AWS Bedrock Configuration
AWS_ACCESS_KEY_ID=your_access_key_id_here
AWS_SECRET_ACCESS_KEY=your_secret_access_key_here
AWS_REGION=us-east-1
AWS_BEDROCK_MODEL=us.anthropic.claude-3-5-sonnet-20241022-v2:0
```

**Security Notes**:
- Never commit `.env` to version control
- Keep your AWS credentials secure
- Consider using AWS IAM roles if deploying to AWS infrastructure

## Step 4: Verify Setup

Run this test script to verify Bedrock is working:

```python
# test_bedrock.py
import asyncio
from infrastructure.bedrock_repository import BedrockRepository

async def test_bedrock():
    bedrock = BedrockRepository()
    
    if not bedrock.is_available():
        print("❌ Bedrock client not initialized. Check your AWS credentials.")
        return
    
    print("✅ Bedrock client initialized successfully!")
    
    try:
        response = await bedrock.generate_text("Say 'Hello from Bedrock!' in a friendly way.")
        print(f"\n📝 Response: {response}")
        print("\n✅ Bedrock is working correctly!")
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    asyncio.run(test_bedrock())
```

Run the test:
```bash
python test_bedrock.py
```

## Step 5: Usage in Your Application

The Bedrock repository is already integrated. Here's how to use it:

```python
from infrastructure.bedrock_repository import BedrockRepository

# Initialize
bedrock = BedrockRepository()

# Check availability
if bedrock.is_available():
    # Generate text
    response = await bedrock.generate_text("Your prompt here")
    print(response)
```

## Current Configuration

- **Model**: Claude 3.5 Sonnet v2 (Inference Profile: `us.anthropic.claude-3-5-sonnet-20241022-v2:0`)
- **Region**: us-east-1 (default)
- **Max Tokens**: 500 (configurable in `bedrock_repository.py`)
- **Temperature**: 0.7 (configurable)
- **Top P**: 0.9 (configurable)

**Note**: AWS Bedrock requires using inference profiles (prefixed with region, e.g., `us.`) instead of direct model IDs for on-demand throughput.

## Troubleshooting

### Error: "AWS credentials not configured"
- Check that `AWS_ACCESS_KEY_ID` and `AWS_SECRET_ACCESS_KEY` are in your `.env` file
- Verify the `.env` file is in the correct directory (`app/backend/`)
- Restart your backend server after adding credentials

### Error: "Could not connect to the endpoint URL"
- Verify your AWS region is correct (default: `us-east-1`)
- Check that Bedrock is available in your region
- Ensure your internet connection is working

### Error: "AccessDeniedException"
- Verify the IAM user has `AmazonBedrockFullAccess` policy
- Check that model access has been granted in the Bedrock console
- Wait a few minutes if you just requested model access

### Error: "ValidationException: The provided model identifier is invalid"
- Verify the model ID in your `.env` matches exactly: `us.anthropic.claude-3-5-sonnet-20241022-v2:0`
- Check that you've requested access to this specific model version

### Error: "Invocation of model ID ... with on-demand throughput isn't supported"
- You need to use an inference profile instead of the direct model ID
- Update your `.env` to use: `AWS_BEDROCK_MODEL=us.anthropic.claude-3-5-sonnet-20241022-v2:0`
- Note the `us.` prefix for the US region inference profile

### Error: "Model use case details have not been submitted for this account"
- **You must submit the Anthropic use case form** (one-time requirement)
- Go to AWS Bedrock Console → Model access
- Click on any Anthropic model and fill out the use case form
- Suggested use case: "AI-powered gaming analytics and match analysis for League of Legends"
- Wait 15-30 minutes after submission
- The form is required even if you already have model access enabled

## Cost Considerations

Claude 3.5 Sonnet v2 pricing (as of Nov 2024):
- **Input**: ~$3.00 per million tokens
- **Output**: ~$15.00 per million tokens

For development/testing with small prompts, costs should be minimal (< $1/month).

## Security Best Practices

1. **Never commit credentials**: Ensure `.env` is in `.gitignore`
2. **Use IAM roles in production**: When deploying to AWS (EC2, ECS, Lambda)
3. **Rotate keys regularly**: Create new access keys periodically
4. **Principle of least privilege**: Only grant necessary permissions
5. **Monitor usage**: Check AWS CloudWatch for unexpected usage

## Additional Resources

- [AWS Bedrock Documentation](https://docs.aws.amazon.com/bedrock/)
- [Claude API Reference](https://docs.anthropic.com/claude/reference)
- [Boto3 Bedrock Documentation](https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/bedrock-runtime.html)
