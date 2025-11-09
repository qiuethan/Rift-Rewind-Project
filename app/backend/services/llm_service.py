"""
LLM Service - Orchestrates AI interactions with user context
Handles interactions with AWS Bedrock for AI-powered analytics
Clean Architecture - Layer 4 (Service/Use Case)
"""
from typing import Optional, Dict, Any, List
from infrastructure.bedrock_repository import BedrockRepository
from repositories.context_repository import ContextRepository
from utils.logger import logger
from utils.champion_mapping import extract_champion_from_text, get_champion_id


class LLMService:
    """Service for AI-powered analytics with user context"""
    
    def __init__(self, bedrock_repository: BedrockRepository, context_repository: ContextRepository):
        """
        Initialize LLM service with dependencies
        
        Args:
            bedrock_repository: Bedrock repository for LLM calls
            context_repository: Context repository for retrieving user data
        """
        self.bedrock = bedrock_repository
        self.context = context_repository
    
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
        # Step 1: Determine what contexts are needed using Haiku (fast & cheap)
        routing = await self.bedrock.classify_context_needs(prompt)
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
        context_prefix = self._build_context_prefix(contexts)
        enriched_prompt = context_prefix + prompt
        
        # Step 4: Generate response with routing
        result = await self.bedrock.generate_text_with_routing(enriched_prompt, use_case=use_case)
        
        # Add context metadata
        result['contexts_used'] = list(contexts.keys())
        result['contexts_data'] = contexts
        
        return result
    
    def _build_context_prefix(self, contexts: Dict[str, Dict[str, Any]]) -> str:
        """Build context prefix for the prompt with metric explanations"""
        # System prompt explaining the AI's role
        prefix = "[SYSTEM]\n"
        prefix += "You are an AI assistant for Rift Rewind, a League of Legends analytics platform.\n"
        
        # Add metric definitions if champion progress is included
        if 'champion_progress' in contexts:
            prefix += "[METRIC DEFINITIONS]\n"
            prefix += "- EPS (End-Game Performance Score): Overall match performance - SKILL\n"
            prefix += "  * Score range: 0-100 (always out of 100)\n"
            prefix += "  * Measures how well the PLAYER performed in the match\n"
            prefix += "  * Combat (40%): KDA, damage dealt, damage taken\n"
            prefix += "  * Economic (30%): Gold earned, CS, gold efficiency\n"
            prefix += "  * Objective (30%): Turret damage, objective participation\n"
            prefix += "  * EPS trending up = Skill improving | EPS trending down = Skill declining\n"
            prefix += "- CPS (Cumulative Power Score): Champion power/itemization - BUILD\n"
            prefix += "  * Score range: 0 to game_duration_in_minutes (scales with game length)\n"
            prefix += "  * Measures champion's accumulated power and strength during the match\n"
            prefix += "  * Economic (45%): Gold and experience advantages\n"
            prefix += "  * Offensive (35%): Damage output and kills\n"
            prefix += "  * Defensive (20%): Survivability and damage mitigation\n"
            prefix += "  * CPS trending up = Building correctly/ahead | CPS trending down = Behind in building or building incorrectly\n"
            prefix += "- Trend: Percentage change per game (positive = improving, negative = declining)\n\n"
        
        if 'summoner' in contexts:
            s = contexts['summoner']
            prefix += f"[PLAYER CONTEXT]\n"
            prefix += f"Player: {s['game_name']} | Region: {s['region']}\n\n"
        
        if 'champion_progress' in contexts:
            cp = contexts['champion_progress']
            prefix += f"[CHAMPION STATS: {cp['champion_name']}]\n"
            prefix += f"Total Games: {cp['total_games']} | Win Rate: {cp['win_rate']:.1f}%\n"
            prefix += f"EPS Score: {cp['avg_eps_score']:.1f}/100 (trend: {cp['eps_trend']:+.1f} per game)\n"
            prefix += f"CPS Score: {cp['avg_cps_score']:.1f}/100 (trend: {cp['cps_trend']:+.1f} per game)\n"
            
            # Add interpretation hints
            if cp['eps_trend'] > 2:
                prefix += f"📈 EPS improving significantly\n"
            elif cp['eps_trend'] < -2:
                prefix += f"📉 EPS declining - skill issue\n"
            
            if cp['cps_trend'] > 2:
                prefix += f"📈 CPS improving significantly\n"
            elif cp['cps_trend'] < -2:
                prefix += f"📉 CPS declining - itemization lacking/issue\n"
            
            prefix += "\n"
        
        if 'match' in contexts:
            m = contexts['match']
            prefix += f"[MATCH CONTEXT]\n"
            prefix += f"Game Type: {m['game_type']} | Champion Played: {m['player_champion']}\n"
            
            # Add player's game stats
            if m.get('player_stats'):
                stats = m['player_stats']
                prefix += f"\n[YOUR GAME STATS]\n"
                prefix += f"Result: {'Victory' if stats['win'] else 'Defeat'}\n"
                prefix += f"KDA: {stats['kills']}/{stats['deaths']}/{stats['assists']}\n"
                kda_ratio = (stats['kills'] + stats['assists']) / max(stats['deaths'], 1)
                prefix += f"KDA Ratio: {kda_ratio:.2f}\n"
                prefix += f"Damage to Champions: {stats['damage']:,}\n"
                prefix += f"Gold Earned: {stats['gold']:,}\n"
                prefix += f"CS: {stats['cs']}\n"
                prefix += f"Game Duration: {m.get('game_duration', 0) // 60} minutes\n"
            
            if m.get('analysis'):
                analysis = m['analysis']
                prefix += f"\n[PERFORMANCE METRICS - ALL 10 PLAYERS]\n"
                prefix += f"EPS (End-Game Performance Score): Measures SKILL - how well you played\n"
                prefix += f"  • Combat (40%): KDA, damage dealt, damage taken\n"
                prefix += f"  • Economic (30%): Gold earned, CS, gold efficiency\n"
                prefix += f"  • Objective (30%): Turret damage, objective participation\n"
                prefix += f"  • Score range: 0-100 (higher is better)\n\n"
                
                prefix += f"CPS (Champion Performance Score): Measures CHAMPION EFFECTIVENESS\n"
                prefix += f"  • How well the champion performed relative to its potential\n"
                prefix += f"  • Considers itemization, build efficiency, champion-specific metrics\n"
                prefix += f"  • Score range: 0-100 (higher is better)\n\n"
                
                # EPS Scores and Breakdown
                if 'rawStats' in analysis and 'epsScores' in analysis['rawStats']:
                    eps_scores = analysis['rawStats']['epsScores']
                    player_champ = m['player_champion']
                    
                    prefix += f"[YOUR PERFORMANCE]\n"
                    if player_champ in eps_scores:
                        player_eps = eps_scores[player_champ]
                        prefix += f"Your EPS Score: {player_eps:.1f}/100\n"
                        
                        # Rank among all 10 players
                        sorted_scores = sorted(eps_scores.items(), key=lambda x: x[1], reverse=True)
                        player_rank = next(i for i, (champ, _) in enumerate(sorted_scores, 1) if champ == player_champ)
                        prefix += f"Your Rank: #{player_rank} out of 10 players (both teams)\n"
                        
                        # Performance interpretation
                        if player_eps >= 70:
                            prefix += f"Performance Level: Excellent! 🌟\n"
                        elif player_eps >= 50:
                            prefix += f"Performance Level: Good ✓\n"
                        elif player_eps >= 30:
                            prefix += f"Performance Level: Average\n"
                        else:
                            prefix += f"Performance Level: Needs improvement\n"
                        
                        # EPS Breakdown from charts
                        if 'charts' in analysis and 'epsBreakdown' in analysis['charts']:
                            breakdown = analysis['charts']['epsBreakdown']
                            datasets = breakdown.get('data', {}).get('datasets', [])
                            labels = breakdown.get('data', {}).get('labels', [])
                            
                            if player_champ in labels:
                                champ_idx = labels.index(player_champ)
                                prefix += f"\nYour Score Breakdown:\n"
                                for dataset in datasets:
                                    score_type = dataset.get('label', 'Unknown')
                                    scores = dataset.get('data', [])
                                    if champ_idx < len(scores):
                                        prefix += f"  • {score_type}: {scores[champ_idx]:.1f}\n"
                        
                        # Show top 3 performers for context
                        prefix += f"\nTop 3 EPS Performers:\n"
                        for i, (champ, score) in enumerate(sorted_scores[:3], 1):
                            marker = " (YOU)" if champ == player_champ else ""
                            prefix += f"  {i}. {champ}: {score:.1f}{marker}\n"
                
                # CPS Scores (Cumulative Power Score from timeline)
                if 'charts' in analysis and 'powerScoreTimeline' in analysis['charts']:
                    timeline = analysis['charts']['powerScoreTimeline']
                    datasets = timeline.get('data', {}).get('datasets', [])
                    
                    # Find player's dataset
                    player_dataset = None
                    for dataset in datasets:
                        if dataset.get('label') == player_champ:
                            player_dataset = dataset
                            break
                    
                    if player_dataset:
                        power_scores = player_dataset.get('data', [])
                        if power_scores:
                            # CPS is the final cumulative power score
                            player_cps = power_scores[-1]
                            game_duration_minutes = len(power_scores) - 1
                            
                            prefix += f"\nYour CPS (Cumulative Power Score): {player_cps:.1f}\n"
                            prefix += f"CPS measures your power accumulation over {game_duration_minutes} minutes.\n"
                            prefix += f"Higher CPS = stronger power curve and game impact over time.\n"
                            
                            # Compare to other players
                            all_final_scores = []
                            for ds in datasets:
                                scores = ds.get('data', [])
                                if scores:
                                    all_final_scores.append((ds.get('label'), scores[-1]))
                            
                            all_final_scores.sort(key=lambda x: x[1], reverse=True)
                            cps_rank = next(i for i, (champ, _) in enumerate(all_final_scores, 1) if champ == player_champ)
                            prefix += f"CPS Rank: #{cps_rank} out of 10 players\n"
                
                # Power Ranking Timeline (performance percentile over time)
                if 'charts' in analysis and 'powerRankingTimeline' in analysis['charts']:
                    ranking_timeline = analysis['charts']['powerRankingTimeline']
                    datasets = ranking_timeline.get('data', {}).get('datasets', [])
                    
                    # Find player's ranking dataset
                    player_ranking_dataset = None
                    for dataset in datasets:
                        if dataset.get('label') == player_champ:
                            player_ranking_dataset = dataset
                            break
                    
                    if player_ranking_dataset:
                        rankings = player_ranking_dataset.get('data', [])
                        if rankings and len(rankings) > 5:
                            prefix += f"\n[PERFORMANCE TIMELINE - Your Power Ranking %]\n"
                            prefix += f"Shows your performance percentile (0-100) at each minute.\n"
                            prefix += f"Higher % = stronger relative to other players at that time.\n\n"
                            
                            # Show key intervals: early (5min), mid (10min, 15min), late (end)
                            intervals = [
                                (5, "Early Game (5 min)"),
                                (10, "Mid Game (10 min)"),
                                (15, "Late Mid (15 min)"),
                                (len(rankings) - 1, f"End Game ({len(rankings)-1} min)")
                            ]
                            
                            for idx, label in intervals:
                                if idx < len(rankings):
                                    rank_pct = rankings[idx]
                                    prefix += f"  • {label}: {rank_pct:.1f}%"
                                    if rank_pct >= 75:
                                        prefix += f" (Dominating)\n"
                                    elif rank_pct >= 50:
                                        prefix += f" (Strong)\n"
                                    elif rank_pct >= 25:
                                        prefix += f" (Struggling)\n"
                                    else:
                                        prefix += f" (Very Weak)\n"
                            
                            # Analyze trend
                            early_avg = sum(rankings[:5]) / min(5, len(rankings))
                            late_avg = sum(rankings[-5:]) / min(5, len(rankings))
                            
                            prefix += f"\nTrend Analysis: "
                            if late_avg > early_avg + 20:
                                prefix += f"Strong scaling - improved significantly as game progressed\n"
                            elif late_avg > early_avg + 10:
                                prefix += f"Good scaling - got stronger over time\n"
                            elif late_avg < early_avg - 20:
                                prefix += f"Fell off - started strong but weakened\n"
                            elif late_avg < early_avg - 10:
                                prefix += f"Declined - performance dropped over time\n"
                            else:
                                prefix += f"Consistent - maintained similar performance level\n"
                
                prefix += f"\nINSTRUCTIONS: Use this data to provide specific, actionable feedback.\n"
                prefix += f"Focus on what the player did well and 1-2 concrete areas to improve.\n"
            prefix += "\n"
        
        return prefix
    
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
        result = await self.bedrock.generate_text_with_routing(enriched_prompt, use_case=use_case)
        
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
        """Build prompt for AI analysis"""
        kda = f"{stats.get('kills', 0)}/{stats.get('deaths', 0)}/{stats.get('assists', 0)}"
        result = "Victory" if stats.get('win') else "Defeat"
        
        prompt = f"""Analyze this League of Legends match performance:

Champion: {stats.get('champion', 'Unknown')}
Role: {stats.get('role', 'Unknown')}
Result: {result}
KDA: {kda}
CS: {stats.get('cs', 0)}
Gold: {stats.get('gold', 0):,}
Damage: {stats.get('damage', 0):,}
Vision Score: {stats.get('vision_score', 0)}
Game Duration: {stats.get('game_duration', 0)} minutes

Provide a concise 3-4 sentence analysis covering:
1. Overall performance assessment
2. Key strengths in this match
3. One specific area for improvement

Keep it constructive and actionable."""

        return prompt
