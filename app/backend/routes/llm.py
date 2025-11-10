"""
LLM/Chat routes for AI-powered interactions
"""
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from services.llm_service import LLMService
from services.player_service import PlayerService
from middleware.auth import get_current_user
from dependency.dependencies import get_player_service, get_llm_service
from infrastructure.bedrock_repository import BedrockRepository
from utils.logger import logger


router = APIRouter(prefix="/api/llm", tags=["llm"])


# ============================================================================
# REQUEST/RESPONSE MODELS
# ============================================================================

class ChatRequest(BaseModel):
    """Request model for chat endpoint"""
    prompt: str = Field(..., description="User's question or prompt")
    match_id: Optional[str] = Field(None, description="Optional match ID for match-specific questions")
    champion_id: Optional[int] = Field(None, description="Optional champion ID for champion-specific questions")
    page_context: Optional[str] = Field(None, description="Optional page context (dashboard, champion_detail, match_detail)")


class ChatResponse(BaseModel):
    """Response model for chat endpoint"""
    text: str = Field(..., description="AI-generated response")
    model_used: str = Field(..., description="Model that generated the response")
    complexity: str = Field(..., description="Prompt complexity (simple/complex)")
    contexts_used: List[str] = Field(..., description="List of contexts that were fetched and used")
    metadata: Optional[Dict[str, Any]] = Field(None, description="Additional metadata")


# ============================================================================
# ROUTES
# ============================================================================

@router.post("/analyze-champion")
async def analyze_champion(
    champion_id: int,
    current_user: str = Depends(get_current_user),
    player_service: PlayerService = Depends(get_player_service),
    llm_service: LLMService = Depends(get_llm_service)
):
    """
    Generate AI-powered analysis for a specific champion
    
    Fetches champion progress context and generates insights about:
    - Performance trends
    - Win rate analysis
    - Improvement suggestions
    - Mastery progress
    """
    logger.info(f"POST /api/llm/analyze-champion - User: {current_user}, Champion ID: {champion_id}")
    
    try:
        # Get user's summoner
        summoner = await player_service.get_summoner(current_user)
        puuid = summoner.puuid
        
        logger.info(f"Analyzing champion {champion_id} for {summoner.game_name}")
        
        # Generate analysis with champion context
        result = await llm_service.analyze_champion(puuid, champion_id)
        
        return {
            "summary": result.get('summary', ''),
            "full_analysis": result.get('full_analysis', ''),
            "model_used": result['model_used'],
            "champion_id": champion_id,
            "contexts_used": result.get('contexts_used', [])
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error analyzing champion: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to analyze champion: {str(e)}"
        )


@router.post("/analyze-match")
async def analyze_match(
    match_id: str,
    current_user: str = Depends(get_current_user),
    player_service: PlayerService = Depends(get_player_service),
    llm_service: LLMService = Depends(get_llm_service)
):
    """
    Generate AI-powered analysis for a specific match
    
    Fetches match context and generates insights about:
    - Performance breakdown
    - Key moments and decisions
    - Areas for improvement
    - Comparison to averages
    """
    logger.info(f"POST /api/llm/analyze-match - User: {current_user}, Match: {match_id}")
    
    try:
        # Get user's summoner
        summoner = await player_service.get_summoner(current_user)
        puuid = summoner.puuid
        
        logger.info(f"Analyzing match {match_id} for {summoner.game_name}")
        
        # Generate analysis with match context
        result = await llm_service.analyze_match(puuid, match_id)
        
        return {
            "summary": result.get('summary', ''),
            "full_analysis": result.get('full_analysis', ''),
            "model_used": result['model_used'],
            "match_id": match_id,
            "contexts_used": result.get('contexts_used', [])
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error analyzing match: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to analyze match: {str(e)}"
        )


@router.get("/health")
async def check_llm_health():
    """Check if LLM service is available"""
    bedrock = BedrockRepository()
    is_available = bedrock.is_available()
    
    return {
        "status": "healthy" if is_available else "unavailable",
        "bedrock_available": is_available
    }
