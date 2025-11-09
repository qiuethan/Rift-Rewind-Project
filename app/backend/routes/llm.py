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

@router.post("/chat", response_model=ChatResponse)
async def chat(
    request: ChatRequest,
    current_user: str = Depends(get_current_user),
    player_service: PlayerService = Depends(get_player_service),
    llm_service: LLMService = Depends(get_llm_service)
):
    """
    AI-powered chat endpoint with smart context routing
    
    The frontend should send:
    - **prompt**: User's question (required)
    - **match_id**: Optional, if user is on a match detail page
    - **champion_id**: Optional, if user is on a champion detail page
    - **page_context**: Optional, for analytics/tracking
    
    The backend will:
    1. Get the user's PUUID from their auth token
    2. Use smart routing to determine what data to fetch
    3. Automatically fetch summoner, champion progress, or match data as needed
    4. Return AI-generated response with appropriate context
    """
    logger.info(f"POST /api/llm/chat - User: {current_user}, Page: {request.page_context}")
    logger.debug(f"Request: {request.dict()}")
    
    try:
        # Get user's summoner to get PUUID
        summoner = await player_service.get_summoner(current_user)
        puuid = summoner.puuid
        
        logger.info(f"User ID: {current_user}")
        logger.info(f"Summoner: {summoner.game_name}#{summoner.tag_line} ({summoner.region})")
        logger.info(f"Generating response for PUUID: {puuid}")
        
        # WORKAROUND: Inject summoner context directly since we already have it
        # This avoids the database query issue
        summoner_context = {
            'game_name': summoner.game_name,
            'region': summoner.region
        }
        
        # Call smart routing service
        result = await llm_service.generate_with_smart_routing(
            puuid=puuid,
            prompt=request.prompt,
            match_id=request.match_id,
            summoner_context_override=summoner_context  # Pass it directly
        )
        
        # Build response
        response = ChatResponse(
            text=result['text'],
            model_used=result['model_used'],
            complexity=result['complexity'],
            contexts_used=result['contexts_used'],
            metadata={
                'page_context': request.page_context,
                'champion_id': request.champion_id,
                'match_id': request.match_id
            }
        )
        
        logger.info(f"Response generated - Model: {response.model_used}, Contexts: {response.contexts_used}")
        return response
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error in chat endpoint: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to generate response: {str(e)}"
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
    
    This is a convenience endpoint that automatically generates
    a comprehensive match analysis without requiring a prompt.
    """
    logger.info(f"POST /api/llm/analyze-match - User: {current_user}, Match: {match_id}")
    
    try:
        # Get user's summoner
        summoner = await player_service.get_summoner(current_user)
        puuid = summoner.puuid
        
        # Get match data
        match_data = await player_service.get_match_by_id(current_user, match_id)
        
        # Generate analysis
        result = await llm_service.analyze_match(puuid, match_data.dict())
        
        return {
            "text": result['text'],
            "model_used": result['model_used'],
            "complexity": result['complexity'],
            "match_id": match_id
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
