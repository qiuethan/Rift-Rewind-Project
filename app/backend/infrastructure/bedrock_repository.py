"""
AWS Bedrock Repository Implementation
Concrete implementation for AWS Bedrock LLM with Prompt Routing (Clean Architecture - Layer 5)
"""
import json
import boto3
from typing import Optional, Dict, Any
from repositories.llm_repository import LLMRepository
from config.settings import settings
from config.bedrock_config import (
    BedrockModels,
    PromptRouterConfig,
    RouterPrompts,
    RiftRewindUseCases
)
from utils.logger import logger


class BedrockRepository(LLMRepository):
    """AWS Bedrock implementation of LLM repository"""
    
    def __init__(self):
        """Initialize Bedrock client"""
        self.client = None
        self._initialize_client()
    
    def _initialize_client(self):
        """Initialize boto3 Bedrock client with credentials"""
        if not settings.AWS_ACCESS_KEY_ID or not settings.AWS_SECRET_ACCESS_KEY:
            logger.warning("AWS credentials not configured")
            return
        
        try:
            self.client = boto3.client(
                service_name='bedrock-runtime',
                region_name=settings.AWS_REGION,
                aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
                aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY
            )
            logger.info(f"AWS Bedrock client initialized (region: {settings.AWS_REGION})")
        except Exception as e:
            logger.error(f"Failed to initialize AWS Bedrock client: {e}")
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
            logger.error(f"Bedrock invocation error: {e}")
            raise
    
    async def classify_context_needs(self, prompt: str) -> Dict[str, Any]:
        """
        Classify what context data is needed for the prompt
        
        Args:
            prompt: User's prompt
            
        Returns:
            Dict with contexts array containing strings and objects:
            {"contexts": ["summoner", {"champion_progress": "Yasuo"}, {"match": "match_id"}]}
        """
        try:
            import json
            context_prompt = RouterPrompts.CONTEXT_ROUTING_PROMPT.format(user_prompt=prompt)
            
            logger.info(f"=== ROUTER PROMPT ===\n{context_prompt}\n=== END ROUTER PROMPT ===")
            
            # Use Haiku for fast context classification
            response = await self._invoke_model(
                model_id=PromptRouterConfig.ROUTER_MODEL,
                prompt=context_prompt,
                max_tokens=100,
                temperature=0.3
            )
            
            logger.info(f"=== ROUTER RESPONSE ===\n{response}\n=== END ROUTER RESPONSE ===")
            
            # Parse JSON response (handle markdown code blocks)
            try:
                # Strip markdown code blocks if present
                cleaned_response = response.strip()
                if cleaned_response.startswith('```'):
                    # Remove ```json or ``` at start
                    cleaned_response = cleaned_response.split('\n', 1)[1] if '\n' in cleaned_response else cleaned_response[3:]
                    # Remove ``` at end
                    if cleaned_response.endswith('```'):
                        cleaned_response = cleaned_response.rsplit('```', 1)[0]
                    cleaned_response = cleaned_response.strip()
                
                logger.info(f"=== CLEANED ROUTER RESPONSE ===\n{cleaned_response}\n=== END CLEANED ===")
                
                result = json.loads(cleaned_response)
                contexts = result.get('contexts', ['summoner'])
                
                # Ensure summoner is always first
                if not contexts or contexts[0] != 'summoner':
                    contexts.insert(0, 'summoner')
                
                routing_result = {'contexts': contexts}
                logger.info(f"Context routing: {routing_result}")
                return routing_result
                
            except json.JSONDecodeError as je:
                logger.warning(f"Failed to parse JSON response: {response}. Error: {je}")
                return {'contexts': ['summoner']}
            
        except Exception as e:
            logger.error(f"Error classifying context needs: {e}")
            return {'contexts': ['summoner']}
    
    async def classify_prompt_complexity(self, prompt: str) -> str:
        """
        Classify prompt complexity to determine which model to use
        
        Args:
            prompt: User's prompt
            
        Returns:
            Complexity level: "simple", "moderate", or "complex"
        """
        try:
            classification_prompt = RouterPrompts.CLASSIFICATION_PROMPT.format(user_prompt=prompt)
            
            # Use Sonnet 3.5 for classification (fast and accurate)
            response = await self._invoke_model(
                model_id=PromptRouterConfig.ROUTER_MODEL,
                prompt=classification_prompt,
                max_tokens=10,
                temperature=0.3
            )
            
            complexity = response.strip().lower()
            
            # Validate response
            if complexity in ["simple", "moderate", "complex"]:
                logger.info(f"Classified prompt as: {complexity}")
                return complexity
            
            logger.warning(f"Invalid classification '{complexity}', defaulting to moderate")
            return "moderate"
            
        except Exception as e:
            logger.error(f"Error classifying prompt: {e}")
            return "moderate"  # Default to moderate on error
    
    async def generate_text_with_routing(self, prompt: str, use_case: Optional[str] = None) -> Dict[str, Any]:
        """
        Generate text using automatic prompt routing
        
        Args:
            prompt: The prompt to send
            use_case: Optional predefined use case (e.g., "match_summary", "greeting")
            
        Returns:
            Dict with 'text', 'model_used', and 'complexity' keys
        """
        if not self.client:
            raise Exception("AWS Bedrock client not initialized")
        
        try:
            # Use Claude Sonnet 4 for all responses (no complexity classification)
            model_id = BedrockModels.CLAUDE_SONNET_4
            max_tokens = 2048
            temperature = 0.7
            
            logger.info(f"Using model: {model_id}")
            
            logger.info(f"=== RESPONSE MODEL PROMPT ===\n{prompt[:500]}...\n=== END RESPONSE PROMPT (truncated) ===")
            
            # Generate response
            text = await self._invoke_model(
                model_id=model_id,
                prompt=prompt,
                max_tokens=max_tokens,
                temperature=temperature
            )
            
            logger.info(f"=== RESPONSE MODEL OUTPUT ===\n{text[:300]}...\n=== END RESPONSE (truncated) ===")
            
            return {
                "text": text,
                "model_used": model_id,
                "complexity": "n/a",  # No longer classifying complexity
                "max_tokens": max_tokens
            }
            
        except Exception as e:
            logger.error(f"Bedrock routing error: {e}")
            raise
    
    async def _invoke_model(
        self,
        model_id: str,
        prompt: str,
        max_tokens: int = 1500,
        temperature: float = 0.7,
        top_p: float = 0.9
    ) -> str:
        """
        Internal method to invoke a specific Bedrock model
        
        Args:
            model_id: Bedrock model ID
            prompt: The prompt
            max_tokens: Maximum tokens to generate
            temperature: Sampling temperature
            top_p: Nucleus sampling parameter
            
        Returns:
            Generated text
        """
        try:
            # Prepare request body for Claude
            # Note: Claude models don't allow both temperature and top_p
            body = json.dumps({
                "anthropic_version": "bedrock-2023-05-31",
                "max_tokens": max_tokens,
                "messages": [
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                "temperature": temperature
                # Only use temperature, not top_p (AWS Bedrock restriction)
            })
            
            # Invoke model
            response = self.client.invoke_model(
                modelId=model_id,
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
            logger.error(f"Bedrock invocation error for model {model_id}: {e}")
            raise
    
    def is_available(self) -> bool:
        """Check if Bedrock client is available"""
        return self.client is not None
