"""
LLM Repository Interface
Defines the contract for LLM operations (Clean Architecture - Layer 4)
"""
from abc import ABC, abstractmethod
from typing import Optional, Dict, Any


class LLMRepository(ABC):
    """Abstract repository for LLM operations"""
    
    @abstractmethod
    async def generate_text(self, prompt: str) -> str:
        """
        Generate text from a prompt using an LLM
        
        Args:
            prompt: The prompt to send to the LLM
            
        Returns:
            Generated text response
            
        Raises:
            Exception: If generation fails
        """
        pass
    
    @abstractmethod
    async def classify_context_needs(self, prompt: str) -> Dict[str, Any]:
        """
        Classify what context data is needed for the prompt
        
        Args:
            prompt: User's prompt
            
        Returns:
            Dict with contexts array containing strings and objects
        """
        pass
    
    @abstractmethod
    async def generate_text_with_routing(
        self, 
        prompt: str, 
        use_case: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Generate text using automatic prompt routing
        
        Args:
            prompt: The prompt to send
            use_case: Optional predefined use case
            
        Returns:
            Dict with 'text', 'model_used', and 'complexity' keys
        """
        pass
    
    @abstractmethod
    def is_available(self) -> bool:
        """
        Check if the LLM service is available and configured
        
        Returns:
            True if LLM is available, False otherwise
        """
        pass
