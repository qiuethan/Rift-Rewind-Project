"""
LLM Prompt Builder Infrastructure
Handles prompt construction and context formatting (Clean Architecture - Layer 5)
"""
from typing import Dict, Any
from utils.logger import logger


class LLMPromptBuilder:
    """Infrastructure for building LLM prompts with context"""
    
    def build_context_prefix(self, contexts: Dict[str, Dict[str, Any]]) -> str:
        """
        Build context prefix for the prompt with metric explanations
        
        Args:
            contexts: Dictionary of context data (summoner, champion_progress, match)
            
        Returns:
            Formatted context prefix string
        """
        # System prompt explaining the AI's role
        prefix = "[SYSTEM]\n"
        prefix += "You are an AI assistant for Rift Rewind, a League of Legends analytics platform.\n"
        
        # Add metric definitions if champion progress is included
        if 'champion_progress' in contexts:
            prefix += self._build_metric_definitions()
        
        if 'summoner' in contexts:
            prefix += self._build_summoner_context(contexts['summoner'])
        
        if 'champion_progress' in contexts:
            prefix += self._build_champion_progress_context(contexts['champion_progress'])
        
        if 'match' in contexts:
            prefix += self._build_match_context(contexts['match'])
        
        return prefix
    
    def _build_metric_definitions(self) -> str:
        """Build metric definitions section"""
        definitions = "[METRIC DEFINITIONS]\n"
        definitions += "- EPS (End-Game Performance Score): Overall match performance - SKILL\n"
        definitions += "  * Score range: 0-100 (always out of 100)\n"
        definitions += "  * Measures how well the PLAYER performed in the match\n"
        definitions += "  * Combat (40%): KDA, damage dealt, damage taken\n"
        definitions += "  * Economic (30%): Gold earned, CS, gold efficiency\n"
        definitions += "  * Objective (30%): Turret damage, objective participation\n"
        definitions += "  * EPS trending up = Skill improving | EPS trending down = Skill declining\n"
        definitions += "- CPS (Cumulative Power Score): Champion power/itemization - BUILD\n"
        definitions += "  * Score range: 0 to game_duration_in_minutes (scales with game length)\n"
        definitions += "  * Measures champion's accumulated power and strength during the match\n"
        definitions += "  * Economic (45%): Gold and experience advantages\n"
        definitions += "  * Offensive (35%): Damage output and kills\n"
        definitions += "  * Defensive (20%): Survivability and damage mitigation\n"
        definitions += "  * CPS trending up = Building correctly/ahead | CPS trending down = Behind in building or building incorrectly\n"
        definitions += "- Trend: Percentage change per game (positive = improving, negative = declining)\n\n"
        return definitions
    
    def _build_summoner_context(self, summoner: Dict[str, Any]) -> str:
        """Build summoner context section"""
        context = f"[PLAYER CONTEXT]\n"
        context += f"Player: {summoner['game_name']} | Region: {summoner['region']}\n\n"
        return context
    
    def _build_champion_progress_context(self, cp: Dict[str, Any]) -> str:
        """Build champion progress context section"""
        context = f"[CHAMPION STATS: {cp['champion_name']}]\n"
        context += f"Total Games: {cp['total_games']} | Win Rate: {cp['win_rate']:.1f}%\n"
        context += f"EPS Score: {cp['avg_eps_score']:.1f}/100 (trend: {cp['eps_trend']:+.1f} per game)\n"
        context += f"CPS Score: {cp['avg_cps_score']:.1f}/1 (normally distributed) (trend: {cp['cps_trend']:+.1f} per game)\n"
        
        # Add interpretation hints
        if cp['eps_trend'] > 2:
            context += f"📈 EPS improving significantly\n"
        elif cp['eps_trend'] < -2:
            context += f"📉 EPS declining - skill issue\n"
        
        if cp['cps_trend'] > 2:
            context += f"📈 CPS improving significantly\n"
        elif cp['cps_trend'] < -2:
            context += f"📉 CPS declining - itemization lacking/issue\n"
        
        context += "\n"
        return context
    
    def _build_match_context(self, m: Dict[str, Any]) -> str:
        """Build match context section"""
        context = f"[MATCH CONTEXT]\n"
        context += f"Game Type: {m['game_type']} | Champion Played: {m['player_champion']}\n"
        
        # Add player's game stats
        if m.get('player_stats'):
            context += self._build_player_stats(m['player_stats'], m.get('game_duration', 0))
        
        if m.get('analysis'):
            context += self._build_match_analysis(m['analysis'], m['player_champion'])
        
        context += "\n"
        return context
    
    def _build_player_stats(self, stats: Dict[str, Any], game_duration: int) -> str:
        """Build player stats section"""
        stats_text = f"\n[YOUR GAME STATS]\n"
        stats_text += f"Result: {'Victory' if stats['win'] else 'Defeat'}\n"
        stats_text += f"KDA: {stats['kills']}/{stats['deaths']}/{stats['assists']}\n"
        kda_ratio = (stats['kills'] + stats['assists']) / max(stats['deaths'], 1)
        stats_text += f"KDA Ratio: {kda_ratio:.2f}\n"
        stats_text += f"Damage to Champions: {stats['damage']:,}\n"
        stats_text += f"Gold Earned: {stats['gold']:,}\n"
        stats_text += f"CS: {stats['cs']}\n"
        stats_text += f"Game Duration: {game_duration // 60} minutes\n"
        return stats_text
    
    def _build_match_analysis(self, analysis: Dict[str, Any], player_champ: str) -> str:
        """Build match analysis section"""
        analysis_text = f"\n[PERFORMANCE METRICS - ALL 10 PLAYERS]\n"
        analysis_text += f"EPS (End-Game Performance Score): Measures SKILL - how well you played\n"
        analysis_text += f"  • Combat (40%): KDA, damage dealt, damage taken\n"
        analysis_text += f"  • Economic (30%): Gold earned, CS, gold efficiency\n"
        analysis_text += f"  • Objective (30%): Turret damage, objective participation\n"
        analysis_text += f"  • Score range: 0-100 (higher is better)\n\n"
        
        analysis_text += f"CPS (Champion Performance Score): Measures CHAMPION EFFECTIVENESS\n"
        analysis_text += f"  • How well the champion performed relative to its potential\n"
        analysis_text += f"  • Considers itemization, build efficiency, champion-specific metrics\n"
        analysis_text += f"  • Score range: 0-1 (higher is better, normally distributed)\n\n"
        
        # EPS Scores and Breakdown
        if 'rawStats' in analysis and 'epsScores' in analysis['rawStats']:
            analysis_text += self._build_eps_breakdown(analysis, player_champ)
        
        # CPS Scores (Cumulative Power Score from timeline)
        if 'charts' in analysis and 'powerScoreTimeline' in analysis['charts']:
            analysis_text += self._build_cps_timeline(analysis['charts']['powerScoreTimeline'], player_champ)
        
        # Power Ranking Timeline
        if 'charts' in analysis and 'powerRankingTimeline' in analysis['charts']:
            analysis_text += self._build_power_ranking_timeline(analysis['charts']['powerRankingTimeline'], player_champ)
        
        analysis_text += f"\nINSTRUCTIONS: Use this data to provide specific, actionable feedback.\n"
        analysis_text += f"Focus on what the player did well and 1-2 concrete areas to improve.\n"
        
        return analysis_text
    
    def _build_eps_breakdown(self, analysis: Dict[str, Any], player_champ: str) -> str:
        """Build EPS breakdown section"""
        eps_scores = analysis['rawStats']['epsScores']
        
        breakdown_text = f"[YOUR PERFORMANCE]\n"
        if player_champ in eps_scores:
            player_eps = eps_scores[player_champ]
            breakdown_text += f"Your EPS Score: {player_eps:.1f}/100\n"
            
            # Rank among all 10 players
            sorted_scores = sorted(eps_scores.items(), key=lambda x: x[1], reverse=True)
            player_rank = next(i for i, (champ, _) in enumerate(sorted_scores, 1) if champ == player_champ)
            breakdown_text += f"Your Rank: #{player_rank} out of 10 players (both teams)\n"
            
            # Performance interpretation
            if player_eps >= 70:
                breakdown_text += f"Performance Level: Excellent! 🌟\n"
            elif player_eps >= 50:
                breakdown_text += f"Performance Level: Good ✓\n"
            elif player_eps >= 30:
                breakdown_text += f"Performance Level: Average\n"
            else:
                breakdown_text += f"Performance Level: Needs improvement\n"
            
            # EPS Breakdown from charts
            if 'charts' in analysis and 'epsBreakdown' in analysis['charts']:
                breakdown = analysis['charts']['epsBreakdown']
                datasets = breakdown.get('data', {}).get('datasets', [])
                labels = breakdown.get('data', {}).get('labels', [])
                
                if player_champ in labels:
                    champ_idx = labels.index(player_champ)
                    breakdown_text += f"\nYour Score Breakdown:\n"
                    for dataset in datasets:
                        score_type = dataset.get('label', 'Unknown')
                        scores = dataset.get('data', [])
                        if champ_idx < len(scores):
                            breakdown_text += f"  • {score_type}: {scores[champ_idx]:.1f}\n"
            
            # Show top 3 performers for context
            breakdown_text += f"\nTop 3 EPS Performers:\n"
            for i, (champ, score) in enumerate(sorted_scores[:3], 1):
                marker = " (YOU)" if champ == player_champ else ""
                breakdown_text += f"  {i}. {champ}: {score:.1f}{marker}\n"
        
        return breakdown_text
    
    def _build_cps_timeline(self, timeline: Dict[str, Any], player_champ: str) -> str:
        """Build CPS timeline section"""
        datasets = timeline.get('data', {}).get('datasets', [])
        
        # Find player's dataset
        player_dataset = None
        for dataset in datasets:
            if dataset.get('label') == player_champ:
                player_dataset = dataset
                break
        
        if not player_dataset:
            return ""
        
        power_scores = player_dataset.get('data', [])
        if not power_scores:
            return ""
        
        # CPS is the final cumulative power score
        player_cps = power_scores[-1]
        game_duration_minutes = len(power_scores) - 1
        
        cps_text = f"\nYour CPS (Cumulative Power Score): {player_cps:.1f}\n"
        cps_text += f"CPS measures your power accumulation over {game_duration_minutes} minutes.\n"
        cps_text += f"Higher CPS = stronger power curve and game impact over time.\n"
        
        # Compare to other players
        all_final_scores = []
        for ds in datasets:
            scores = ds.get('data', [])
            if scores:
                all_final_scores.append((ds.get('label'), scores[-1]))
        
        all_final_scores.sort(key=lambda x: x[1], reverse=True)
        cps_rank = next(i for i, (champ, _) in enumerate(all_final_scores, 1) if champ == player_champ)
        cps_text += f"CPS Rank: #{cps_rank} out of 10 players\n"
        
        return cps_text
    
    def _build_power_ranking_timeline(self, ranking_timeline: Dict[str, Any], player_champ: str) -> str:
        """Build power ranking timeline section"""
        datasets = ranking_timeline.get('data', {}).get('datasets', [])
        
        # Find player's ranking dataset
        player_ranking_dataset = None
        for dataset in datasets:
            if dataset.get('label') == player_champ:
                player_ranking_dataset = dataset
                break
        
        if not player_ranking_dataset:
            return ""
        
        rankings = player_ranking_dataset.get('data', [])
        if not rankings or len(rankings) <= 5:
            return ""
        
        ranking_text = f"\n[PERFORMANCE TIMELINE - Your Power Ranking %]\n"
        ranking_text += f"Shows your performance percentile (0-100) at each minute.\n"
        ranking_text += f"Higher % = stronger relative to other players at that time.\n\n"
        
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
                ranking_text += f"  • {label}: {rank_pct:.1f}%"
                if rank_pct >= 75:
                    ranking_text += f" (Dominating)\n"
                elif rank_pct >= 50:
                    ranking_text += f" (Strong)\n"
                elif rank_pct >= 25:
                    ranking_text += f" (Struggling)\n"
                else:
                    ranking_text += f" (Very Weak)\n"
        
        # Analyze trend
        early_avg = sum(rankings[:5]) / min(5, len(rankings))
        late_avg = sum(rankings[-5:]) / min(5, len(rankings))
        
        ranking_text += f"\nTrend Analysis: "
        if late_avg > early_avg + 20:
            ranking_text += f"Strong scaling - improved significantly as game progressed\n"
        elif late_avg > early_avg + 10:
            ranking_text += f"Good scaling - got stronger over time\n"
        elif late_avg < early_avg - 20:
            ranking_text += f"Fell off - started strong but weakened\n"
        elif late_avg < early_avg - 10:
            ranking_text += f"Declined - performance dropped over time\n"
        else:
            ranking_text += f"Consistent - maintained similar performance level\n"
        
        return ranking_text
    
    def build_analysis_prompt(self, stats: Dict[str, Any]) -> str:
        """
        Build prompt for AI match analysis
        
        Args:
            stats: Player statistics dictionary
            
        Returns:
            Formatted analysis prompt
        """
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
