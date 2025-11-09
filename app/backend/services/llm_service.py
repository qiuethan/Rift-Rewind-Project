"""
LLM Service - Orchestrates AI interactions with user context
Handles interactions with AWS Bedrock for AI-powered analytics
Clean Architecture - Layer 4 (Service/Use Case)
"""
from typing import Optional, Dict, Any, List
from repositories.llm_repository import LLMRepository
from repositories.context_repository import ContextRepository
from infrastructure.llm_prompt_builder import LLMPromptBuilder
from utils.logger import logger
from utils.champion_mapping import extract_champion_from_text, get_champion_id


class LLMService:
    """Service for AI-powered analytics with user context"""
    
    def __init__(
        self, 
        llm_repository: LLMRepository, 
        context_repository: ContextRepository,
        prompt_builder: LLMPromptBuilder
    ):
        """
        Initialize LLM service with dependencies
        
        Args:
            llm_repository: LLM repository for AI calls
            context_repository: Context repository for retrieving user data
            prompt_builder: Infrastructure for building prompts
        """
        self.llm = llm_repository
        self.context = context_repository
        self.prompt_builder = prompt_builder
    
    async def get_summoner_context(self, puuid: str) -> Optional[Dict[str, Any]]:
        """Delegate to context repository"""
        return await self.context.get_summoner_context(puuid)
    
    async def get_champion_progress_context(self, puuid: str, champion_id: int) -> Optional[Dict[str, Any]]:
        """Delegate to context repository"""
        return await self.context.get_champion_progress_context(puuid, champion_id)
    
    async def get_match_context(self, puuid: str, match_id: str) -> Optional[Dict[str, Any]]:
        """Delegate to context repository"""
        return await self.context.get_match_context(puuid, match_id)
    
    # Alias for backward compatibility
    async def get_user_context(self, puuid: str) -> Optional[Dict[str, Any]]:
        """Alias for get_summoner_context"""
        return await self.get_summoner_context(puuid)
    
    async def generate_with_smart_routing(
        self,
        puuid: str,
        prompt: str,
        match_id: Optional[str] = None,
        use_case: Optional[str] = None,
        summoner_context_override: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Generate AI response with smart context routing
        Automatically determines what contexts are needed and fetches them
        
        Args:
            puuid: Player UUID
            prompt: User's prompt/question
            match_id: Optional match ID if discussing a specific match
            use_case: Optional predefined use case for routing
            
        Returns:
            Dict with 'text', 'model_used', 'complexity', 'contexts_used'
        """
        # Step 1: Determine what contexts are needed
        routing = await self.llm.classify_context_needs(prompt)
        logger.info(f"Smart routing: {routing}")
        
        contexts_array = routing['contexts']
        
        # Step 2: Parse contexts array and fetch needed data
        contexts = {}
        
        for ctx in contexts_array:
            # String context (e.g., "summoner")
            if isinstance(ctx, str):
                if ctx == "summoner":
                    # Use override if provided, otherwise query database
                    if summoner_context_override:
                        contexts['summoner'] = summoner_context_override
                        logger.info(f"Using summoner context override: {summoner_context_override}")
                    else:
                        summoner_ctx = await self.get_summoner_context(puuid)
                        if summoner_ctx:
                            contexts['summoner'] = summoner_ctx
            
            # Object context (e.g., {"champion_progress": "Yasuo"})
            elif isinstance(ctx, dict):
                if "champion_progress" in ctx:
                    champion_name = ctx["champion_progress"]
                    if champion_name:
                        champion_id = get_champion_id(champion_name)
                        if champion_id:
                            progress_ctx = await self.get_champion_progress_context(puuid, champion_id)
                            if progress_ctx:
                                contexts['champion_progress'] = progress_ctx
                                logger.info(f"Fetched champion progress for {champion_name} (ID: {champion_id})")
                        else:
                            logger.warning(f"Champion '{champion_name}' not found in mapping")
                
                elif "match" in ctx:
                    # Check if match_id was provided
                    if match_id:
                        match_ctx = await self.get_match_context(puuid, match_id)
                        if match_ctx:
                            contexts['match'] = match_ctx
                    else:
                        logger.warning("Match context needed but no match_id provided")
        
        # Step 3: Build enriched prompt with all contexts
        context_prefix = self.prompt_builder.build_context_prefix(contexts)
        enriched_prompt = context_prefix + prompt
        
        # Step 4: Generate response with routing
        result = await self.llm.generate_text_with_routing(enriched_prompt, use_case=use_case)
        
        # Add context metadata
        result['contexts_used'] = list(contexts.keys())
        result['contexts_data'] = contexts
        
        return result
    
    
    async def generate_with_context(
        self,
        puuid: str,
        prompt: str,
        use_case: Optional[str] = None,
        additional_context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Generate AI response with user context included
        
        Args:
            puuid: Player UUID
            prompt: User's prompt/question
            use_case: Optional predefined use case for routing
            additional_context: Optional additional context to include
            
        Returns:
            Dict with 'text', 'model_used', 'complexity', and 'user_context'
        """
        # Get user context
        user_context = await self.get_user_context(puuid)
        
        if not user_context:
            logger.warning(f"Proceeding without user context for {puuid}")
            user_context = {'game_name': 'Unknown', 'region': 'Unknown'}
        
        # Build enriched prompt with context
        context_prefix = f"[Player: {user_context['game_name']} | Region: {user_context['region']}]\n\n"
        
        if additional_context:
            for key, value in additional_context.items():
                context_prefix += f"[{key}: {value}]\n"
            context_prefix += "\n"
        
        enriched_prompt = context_prefix + prompt
        
        logger.info(f"Generating response for {user_context['game_name']} with use_case: {use_case}")
        
        # Generate response with routing
        result = await self.llm.generate_text_with_routing(enriched_prompt, use_case=use_case)
        
        # Add user context to result
        result['user_context'] = user_context
        
        return result
    
    async def analyze_match(
        self,
        puuid: str,
        match_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Generate AI-powered match analysis with user context
        
        Args:
            puuid: Player UUID
            match_data: Complete match data from Riot API
            
        Returns:
            Analysis result with text and metadata
        """
        # Extract player stats
        player_stats = self._extract_player_stats(match_data, puuid)
        
        # Build analysis prompt
        prompt = self._build_analysis_prompt(player_stats)
        
        # Generate with context
        return await self.generate_with_context(
            puuid=puuid,
            prompt=prompt,
            use_case="match_summary",
            additional_context={'champion': player_stats.get('champion')}
        )
    
    def _extract_player_stats(
        self,
        match_data: Dict[str, Any],
        player_puuid: str
    ) -> Dict[str, Any]:
        """Extract relevant player statistics from match data"""
        info = match_data.get('info', {})
        participants = info.get('participants', [])
        
        # Find player's data
        player_data = None
        for participant in participants:
            if participant.get('puuid') == player_puuid:
                player_data = participant
                break
        
        if not player_data:
            return {}
        
        return {
            'champion': player_data.get('championName', 'Unknown'),
            'role': player_data.get('teamPosition', 'Unknown'),
            'kills': player_data.get('kills', 0),
            'deaths': player_data.get('deaths', 0),
            'assists': player_data.get('assists', 0),
            'cs': player_data.get('totalMinionsKilled', 0) + player_data.get('neutralMinionsKilled', 0),
            'gold': player_data.get('goldEarned', 0),
            'damage': player_data.get('totalDamageDealtToChampions', 0),
            'vision_score': player_data.get('visionScore', 0),
            'game_duration': info.get('gameDuration', 0) // 60,  # Convert to minutes
            'win': player_data.get('win', False)
        }
    
    def _build_analysis_prompt(self, stats: Dict[str, Any]) -> str:
        """Build prompt for AI analysis - delegates to prompt builder"""
        return self.prompt_builder.build_analysis_prompt(stats)
