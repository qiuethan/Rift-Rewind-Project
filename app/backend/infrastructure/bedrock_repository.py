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
        DEPRECATED: Context routing removed. Contexts are now determined by endpoint.
        This method is kept for backward compatibility but returns empty contexts.
        
        Args:
            prompt: User's prompt
            
        Returns:
            Dict with empty contexts array
        """
        logger.warning("classify_context_needs called but routing is deprecated")
        return {'contexts': []}
    
    async def generate_text_with_routing(self, prompt: str, use_case: Optional[str] = None) -> Dict[str, Any]:
        """
        Generate both a 3-line summary and full analysis using Claude Sonnet 4
        Note: 'routing' is deprecated but method name kept for backward compatibility
        
        Args:
            prompt: The prompt to send
            use_case: Optional use case label for logging
            
        Returns:
            Dict with 'summary', 'full_analysis', 'model_used' keys
        """
        if not self.client:
            raise Exception("AWS Bedrock client not initialized")
        
        try:
            # Use Claude Sonnet 4 for all responses
            model_id = BedrockModels.CLAUDE_SONNET_4
            max_tokens = 3072  # Increased for both summary and full analysis
            temperature = 0.7
            
            logger.info(f"Generating summary + analysis with {model_id} (use_case: {use_case})")
            logger.debug(f"Prompt preview: {prompt[:200]}...")
            
            # Enhanced prompt to request both summary and full analysis
            enhanced_prompt = f"""{prompt}

Please provide your response in the following format:

## SUMMARY
[Provide a concise 3-line summary of the key insights]

## FULL ANALYSIS
[Provide a comprehensive, detailed analysis with specific recommendations and observations]
"""
            
            # Generate response
            text = await self._invoke_model(
                model_id=model_id,
                prompt=enhanced_prompt,
                max_tokens=max_tokens,
                temperature=temperature
            )
            
            logger.debug(f"Response preview: {text[:200]}...")
            
            # Parse the response to extract summary and full analysis
            summary, full_analysis = self._parse_summary_and_analysis(text)
            
            return {
                "summary": summary,
                "full_analysis": full_analysis,
                "text": text,  # Keep original for backward compatibility
                "model_used": model_id,
                "max_tokens": max_tokens
            }
            
        except Exception as e:
            logger.error(f"Bedrock generation error: {e}")
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
    
    def _parse_summary_and_analysis(self, text: str) -> tuple[str, str]:
        """
        Parse the LLM response to extract summary and full analysis sections
        
        Args:
            text: Raw LLM response
            
        Returns:
            Tuple of (summary, full_analysis)
        """
        try:
            # Look for ## SUMMARY and ## FULL ANALYSIS markers
            summary_marker = "## SUMMARY"
            analysis_marker = "## FULL ANALYSIS"
            
            summary = ""
            full_analysis = ""
            
            if summary_marker in text and analysis_marker in text:
                # Extract summary section
                summary_start = text.index(summary_marker) + len(summary_marker)
                analysis_start = text.index(analysis_marker)
                summary = text[summary_start:analysis_start].strip()
                
                # Extract full analysis section
                full_analysis = text[analysis_start + len(analysis_marker):].strip()
            else:
                # Fallback: if markers not found, split the text
                # First 3 lines as summary, rest as full analysis
                lines = text.strip().split('\n')
                summary_lines = []
                analysis_lines = []
                
                # Take first few non-empty lines for summary
                line_count = 0
                for i, line in enumerate(lines):
                    if line.strip():
                        if line_count < 3:
                            summary_lines.append(line)
                            line_count += 1
                        else:
                            analysis_lines.extend(lines[i:])
                            break
                
                summary = '\n'.join(summary_lines)
                full_analysis = '\n'.join(analysis_lines) if analysis_lines else text
            
            # Clean up any remaining markdown headers
            summary = summary.replace('## SUMMARY', '').replace('#', '').strip()
            full_analysis = full_analysis.replace('## FULL ANALYSIS', '').replace('## Analysis', '').strip()
            
            return summary, full_analysis
            
        except Exception as e:
            logger.warning(f"Failed to parse summary/analysis sections: {e}")
            # Fallback: return first 3 lines as summary, rest as analysis
            lines = text.strip().split('\n')
            summary = '\n'.join(lines[:3])
            full_analysis = '\n'.join(lines[3:]) if len(lines) > 3 else text
            return summary, full_analysis
    
    def is_available(self) -> bool:
        """Check if Bedrock client is available"""
        return self.client is not None
