# AWS Bedrock Setup Guide

This guide will help you configure AWS Bedrock for AI-powered match analysis in Rift Rewind.

## 🎯 What is AWS Bedrock?

AWS Bedrock is Amazon's managed service for foundation models (LLMs). We use it to generate:
- Match performance analysis
- Champion recommendations
- Gameplay insights

## 📋 Prerequisites

- AWS Account
- AWS CLI installed (optional but recommended)
- IAM user with Bedrock access

## 🔧 Setup Steps

### 1. Create AWS Account

If you don't have one:
1. Go to [aws.amazon.com](https://aws.amazon.com)
2. Click "Create an AWS Account"
3. Follow the registration process

### 2. Enable Bedrock Model Access

1. Sign in to AWS Console
2. Navigate to **Amazon Bedrock**
3. Go to **Model access** in the left sidebar
4. Click **Manage model access**
5. Enable access to:
   - ✅ **Anthropic Claude 3.5 Sonnet v2** (recommended)
   - Or any other Claude model you prefer
6. Click **Save changes**
7. Wait for access to be granted (usually instant)

### 3. Create IAM User for API Access

#### Option A: Using AWS Console

1. Go to **IAM** → **Users** → **Create user**
2. User name: `rift-rewind-bedrock`
3. Select **Programmatic access**
4. Click **Next: Permissions**
5. Click **Attach policies directly**
6. Search and select: `AmazonBedrockFullAccess`
7. Click **Next** → **Create user**
8. **Important:** Save the credentials:
   - Access Key ID
   - Secret Access Key

#### Option B: Using AWS CLI

```bash
# Create IAM user
aws iam create-user --user-name rift-rewind-bedrock

# Attach Bedrock policy
aws iam attach-user-policy \
  --user-name rift-rewind-bedrock \
  --policy-arn arn:aws:iam::aws:policy/AmazonBedrockFullAccess

# Create access key
aws iam create-access-key --user-name rift-rewind-bedrock
```

### 4. Configure Backend

Edit your `backend/.env` file:

```env
# AWS Bedrock Configuration
AWS_ACCESS_KEY_ID=AKIAIOSFODNN7EXAMPLE
AWS_SECRET_ACCESS_KEY=wJalrXUtnFEMI/K7MDENG/bPxRfiCYEXAMPLEKEY
AWS_REGION=us-east-1
AWS_BEDROCK_MODEL=anthropic.claude-3-5-sonnet-20241022-v2:0
```

**Available Regions:**
- `us-east-1` (N. Virginia) - Recommended
- `us-west-2` (Oregon)
- `eu-west-1` (Ireland)
- `ap-southeast-1` (Singapore)

**Available Models:**
- `anthropic.claude-3-5-sonnet-20241022-v2:0` - Latest, best performance
- `anthropic.claude-3-5-sonnet-20240620-v1:0` - Previous version
- `anthropic.claude-3-haiku-20240307-v1:0` - Faster, cheaper
- `anthropic.claude-3-opus-20240229-v1:0` - Most capable, slower

### 5. Test the Configuration

Start your backend:
```bash
cd backend
./run.sh
```

You should see:
```
✅ AWS Bedrock client initialized (region: us-east-1)
```

## 💰 Pricing

AWS Bedrock pricing (as of 2024):

**Claude 3.5 Sonnet v2:**
- Input: $3.00 per 1M tokens
- Output: $15.00 per 1M tokens

**Estimated costs for Rift Rewind:**
- Match analysis: ~500 tokens per request
- Cost per analysis: ~$0.01
- 1000 analyses: ~$10

**Free Tier:**
- AWS Free Tier does NOT include Bedrock
- You'll be charged for usage from day 1

## 🔒 Security Best Practices

### 1. Use IAM Roles (Production)

For production deployments, use IAM roles instead of access keys:

```python
# The boto3 client will automatically use IAM role credentials
self.client = boto3.client(
    service_name='bedrock-runtime',
    region_name=settings.AWS_REGION
)
```

### 2. Restrict IAM Permissions

Create a custom policy with minimal permissions:

```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Action": [
        "bedrock:InvokeModel"
      ],
      "Resource": [
        "arn:aws:bedrock:us-east-1::foundation-model/anthropic.claude-3-5-sonnet-20241022-v2:0"
      ]
    }
  ]
}
```

### 3. Never Commit Credentials

- ✅ Add `.env` to `.gitignore`
- ✅ Use environment variables
- ❌ Never hardcode credentials
- ❌ Never commit `.env` files

### 4. Rotate Keys Regularly

```bash
# Deactivate old key
aws iam update-access-key \
  --user-name rift-rewind-bedrock \
  --access-key-id OLD_KEY_ID \
  --status Inactive

# Create new key
aws iam create-access-key --user-name rift-rewind-bedrock

# Delete old key after testing
aws iam delete-access-key \
  --user-name rift-rewind-bedrock \
  --access-key-id OLD_KEY_ID
```

## 🧪 Testing

### Test Match Analysis

```python
from services.llm_service import bedrock_service

# Test with sample data
match_data = {
    'info': {
        'gameDuration': 1800,
        'participants': [
            {
                'puuid': 'test-puuid',
                'championName': 'Ahri',
                'teamPosition': 'MIDDLE',
                'kills': 10,
                'deaths': 3,
                'assists': 8,
                'totalMinionsKilled': 180,
                'neutralMinionsKilled': 20,
                'goldEarned': 12000,
                'totalDamageDealtToChampions': 25000,
                'visionScore': 35,
                'win': True
            }
        ]
    }
}

analysis = await bedrock_service.generate_match_analysis(
    match_data=match_data,
    player_puuid='test-puuid'
)
print(analysis)
```

### Expected Output

```
Strong performance with a 10/3/8 KDA on Ahri in the mid lane. Your CS of 200 and 
25k damage output demonstrate solid farming and team fight presence. The high vision 
score of 35 shows good map awareness. To improve further, focus on converting your 
gold lead into more objective control and consider roaming earlier to impact side lanes.
```

## 🐛 Troubleshooting

### Error: "Could not connect to the endpoint URL"

**Cause:** Wrong region or model not available in region

**Solution:**
```env
# Try a different region
AWS_REGION=us-west-2
```

### Error: "AccessDeniedException"

**Cause:** IAM user lacks permissions or model access not enabled

**Solution:**
1. Check IAM policy includes `bedrock:InvokeModel`
2. Verify model access is enabled in Bedrock console

### Error: "ValidationException: The provided model identifier is invalid"

**Cause:** Model ID is incorrect or model not available

**Solution:**
```bash
# List available models
aws bedrock list-foundation-models --region us-east-1
```

### Warning: "AWS credentials not configured"

**Cause:** Environment variables not set

**Solution:**
1. Check `.env` file exists
2. Verify `AWS_ACCESS_KEY_ID` and `AWS_SECRET_ACCESS_KEY` are set
3. Restart the server

## 📊 Monitoring Usage

### View Costs in AWS Console

1. Go to **AWS Cost Explorer**
2. Filter by service: **Amazon Bedrock**
3. View daily/monthly costs

### Set Up Billing Alerts

1. Go to **AWS Billing** → **Budgets**
2. Click **Create budget**
3. Set monthly limit (e.g., $10)
4. Add email notification

### Track API Calls

```python
# Add logging to llm_service.py
import logging

logger = logging.getLogger(__name__)

async def _invoke_bedrock(self, prompt: str) -> str:
    logger.info(f"Bedrock API call - Model: {settings.AWS_BEDROCK_MODEL}")
    logger.info(f"Prompt length: {len(prompt)} chars")
    
    response = self.client.invoke_model(...)
    
    logger.info(f"Response length: {len(response_text)} chars")
    return response_text
```

## 🚀 Alternative Models

### Use Claude 3 Haiku (Faster, Cheaper)

```env
AWS_BEDROCK_MODEL=anthropic.claude-3-haiku-20240307-v1:0
```

**Pros:**
- 3x cheaper
- 2x faster
- Good for simple analysis

**Cons:**
- Less detailed insights
- Shorter responses

### Use Claude 3 Opus (Most Capable)

```env
AWS_BEDROCK_MODEL=anthropic.claude-3-opus-20240229-v1:0
```

**Pros:**
- Best quality analysis
- Most detailed insights
- Better reasoning

**Cons:**
- 3x more expensive
- Slower responses

## 📚 Resources

- [AWS Bedrock Documentation](https://docs.aws.amazon.com/bedrock/)
- [Anthropic Claude Models](https://docs.anthropic.com/claude/docs)
- [AWS Bedrock Pricing](https://aws.amazon.com/bedrock/pricing/)
- [boto3 Bedrock Documentation](https://boto3.amazonaws.com/v1/documentation/api/latest/reference/services/bedrock-runtime.html)

## ✅ Checklist

Before going live:
- [ ] AWS account created
- [ ] Bedrock model access enabled
- [ ] IAM user created with minimal permissions
- [ ] Credentials added to `.env`
- [ ] Backend starts without errors
- [ ] Test analysis generated successfully
- [ ] Billing alerts configured
- [ ] `.env` in `.gitignore`

## 🎉 You're Ready!

Your backend is now configured to use AWS Bedrock for AI-powered match analysis!

Test it by:
1. Starting the backend: `./run.sh`
2. Making a match analysis request
3. Checking the AI-generated insights

Happy analyzing! 🎮
