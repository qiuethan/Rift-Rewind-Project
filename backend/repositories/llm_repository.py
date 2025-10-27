"""
LLM Repository Interface
Defines the contract for LLM operations (Clean Architecture - Layer 4)
"""
from abc import ABC, abstractmethod
from typing import Optional


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
    def is_available(self) -> bool:
        """
        Check if the LLM service is available and configured
        
        Returns:
            True if LLM is available, False otherwise
        """
        pass
