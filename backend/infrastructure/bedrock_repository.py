"""
AWS Bedrock Repository Implementation
Concrete implementation for AWS Bedrock LLM (Clean Architecture - Layer 5)
"""
import json
import boto3
from typing import Optional
from repositories.llm_repository import LLMRepository
from config.settings import settings


class BedrockRepository(LLMRepository):
    """AWS Bedrock implementation of LLM repository"""
    
    def __init__(self):
        """Initialize Bedrock client"""
        self.client = None
        self._initialize_client()
    
    def _initialize_client(self):
        """Initialize boto3 Bedrock client with credentials"""
        if not settings.AWS_ACCESS_KEY_ID or not settings.AWS_SECRET_ACCESS_KEY:
            print("⚠️  Warning: AWS credentials not configured")
            return
        
        try:
            self.client = boto3.client(
                service_name='bedrock-runtime',
                region_name=settings.AWS_REGION,
                aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
                aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY
            )
            print(f"✅ AWS Bedrock client initialized (region: {settings.AWS_REGION})")
        except Exception as e:
            print(f"❌ Failed to initialize AWS Bedrock client: {e}")
            self.client = None
    
    async def generate_text(self, prompt: str) -> str:
        """
        Generate text using AWS Bedrock
        
        Args:
            prompt: The prompt to send to Claude
            
        Returns:
            Generated text response
            
        Raises:
            Exception: If generation fails
        """
        if not self.client:
            raise Exception("AWS Bedrock client not initialized")
        
        try:
            # Prepare request body for Claude
            body = json.dumps({
                "anthropic_version": "bedrock-2023-05-31",
                "max_tokens": 500,
                "messages": [
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                "temperature": 0.7,
                "top_p": 0.9
            })
            
            # Invoke model
            response = self.client.invoke_model(
                modelId=settings.AWS_BEDROCK_MODEL,
                body=body,
                contentType='application/json',
                accept='application/json'
            )
            
            # Parse response
            response_body = json.loads(response['body'].read())
            
            # Extract text from Claude response
            if 'content' in response_body and len(response_body['content']) > 0:
                return response_body['content'][0]['text']
            
            return "No response generated"
        
        except Exception as e:
            print(f"❌ Bedrock invocation error: {e}")
            raise
    
    def is_available(self) -> bool:
        """Check if Bedrock client is available"""
        return self.client is not None
