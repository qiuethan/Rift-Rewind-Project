"""
LLM Prompt Builder Infrastructure
Handles prompt construction and context formatting (Clean Architecture - Layer 5)
"""
from typing import Dict, Any
from utils.logger import logger
from infrastructure.prompts.system_prompts import (
    HEIMERDINGER_SYSTEM_PROMPT,
    HEIMERDINGER_ANALYSIS_INSTRUCTIONS
)
from infrastructure.prompts.metric_definitions import (
    METRIC_DEFINITIONS,
    MATCH_ANALYSIS_HEADER
)
from infrastructure.prompts.prt_prompts import (
    PRT_HEADER,
    PRT_GAME_PHASES_HEADER,
    PRT_TREND_HEADER,
    PRT_TREND_SCALING_UP,
    PRT_TREND_FALLING_OFF,
    PRT_TREND_CONSISTENT,
    PRT_ALL_PLAYERS_HEADER,
    PRT_TOP_PERFORMERS,
    PRT_BOTTOM_PERFORMERS,
    PRT_YOUR_POSITION
)
from infrastructure.prompts.cps_prompts import (
    CPS_TIMELINE_HEADER,
    CPS_ALL_PLAYERS_HEADER,
    CPS_YOUR_ANALYSIS_HEADER,
    CPS_YOUR_RANK,
    CPS_YOUR_AVG,
    CPS_YOUR_FINAL,
    CPS_YOUR_GROWTH
)
from infrastructure.prompts.context_headers import (
    PLAYER_CONTEXT_HEADER,
    PLAYER_INFO,
    CHAMPION_STATS_HEADER,
    CHAMPION_BASIC_STATS,
    CHAMPION_EPS,
    CHAMPION_CPS,
    EPS_IMPROVING,
    EPS_DECLINING,
    CPS_IMPROVING,
    CPS_DECLINING,
    MATCH_CONTEXT_HEADER,
    MATCH_BASIC_INFO,
    MATCH_YOUR_TEAM_HEADER,
    MATCH_ENEMY_TEAM_HEADER,
    MATCH_TEAM_PLAYER,
    PLAYER_STATS_HEADER,
    PLAYER_STATS_RESULT,
    PLAYER_STATS_KDA,
    PLAYER_STATS_KDA_RATIO,
    PLAYER_STATS_DAMAGE,
    PLAYER_STATS_GOLD,
    PLAYER_STATS_CS,
    PLAYER_STATS_DURATION,
    PLAYER_PROFILE_HEADER,
    PLAYER_PROFILE_INFO,
    PLAYER_PROFILE_LEVEL,
    PLAYER_PROFILE_CHAMPS,
    CHAMPION_DETAILED_HEADER,
    CHAMPION_DETAILED_GAMES,
    CHAMPION_DETAILED_SCORES,
    CHAMPION_DETAILED_MASTERY,
    CHAMPION_DETAILED_MASTERY_NA,
    MATCH_DETAILED_HEADER,
    MATCH_DETAILED_INFO,
    MATCH_DETAILED_DURATION,
    RECENT_PERFORMANCE_HEADER,
    RECENT_PERFORMANCE_WIN_RATE,
    RECENT_PERFORMANCE_KDA,
    RECENT_PERFORMANCE_TREND,
    RECENT_PERFORMANCE_STREAK
)
from infrastructure.prompts.eps_prompts import (
    EPS_BREAKDOWN_HEADER,
    EPS_YOUR_SCORE,
    EPS_YOUR_RANK,
    EPS_LEVEL_EXCELLENT,
    EPS_LEVEL_GOOD,
    EPS_LEVEL_AVERAGE,
    EPS_LEVEL_NEEDS_IMPROVEMENT,
    EPS_BREAKDOWN_SECTION,
    EPS_BREAKDOWN_ITEM,
    EPS_TOP_PERFORMERS_HEADER,
    EPS_TOP_PERFORMER_ITEM,
    CPS_YOUR_SCORE_HEADER,
    CPS_DESCRIPTION,
    CPS_EXPLANATION,
    CPS_RANK
)


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
        prefix += HEIMERDINGER_SYSTEM_PROMPT
        prefix += "\n"
        
        # Add metric definitions if champion progress or match context is included
        if 'champion_progress' in contexts or 'match' in contexts or 'champion_detailed' in contexts:
            prefix += self._build_metric_definitions()
        
        if 'summoner' in contexts:
            prefix += self._build_summoner_context(contexts['summoner'])
        
        if 'summoner_overview' in contexts:
            prefix += self._build_summoner_overview_context(contexts['summoner_overview'])
        
        if 'champion_progress' in contexts:
            prefix += self._build_champion_progress_context(contexts['champion_progress'])
        
        if 'champion_detailed' in contexts:
            prefix += self._build_champion_detailed_context(contexts['champion_detailed'])
        
        if 'recent_performance' in contexts:
            prefix += self._build_recent_performance_context(contexts['recent_performance'])
        
        if 'match' in contexts:
            prefix += self._build_match_context(contexts['match'])
        
        return prefix
    
    def _build_metric_definitions(self) -> str:
        """Build metric definitions section"""
        return METRIC_DEFINITIONS
    
    def _build_summoner_context(self, summoner: Dict[str, Any]) -> str:
        """Build summoner context section"""
        context = PLAYER_CONTEXT_HEADER
        context += PLAYER_INFO.format(
            game_name=summoner['game_name'],
            region=summoner['region']
        )
        return context
    
    def _build_champion_progress_context(self, cp: Dict[str, Any]) -> str:
        """Build champion progress context section"""
        context = CHAMPION_STATS_HEADER.format(champion_name=cp['champion_name'])
        context += CHAMPION_BASIC_STATS.format(
            total_games=cp['total_games'],
            win_rate=cp['win_rate']
        )
        context += CHAMPION_EPS.format(
            eps=cp['avg_eps_score'],
            trend=cp['eps_trend']
        )
        context += CHAMPION_CPS.format(
            cps=cp['avg_cps_score'],
            trend=cp['cps_trend']
        )
        
        # Add interpretation hints
        if cp['eps_trend'] > 2:
            context += EPS_IMPROVING
        elif cp['eps_trend'] < -2:
            context += EPS_DECLINING
        
        if cp['cps_trend'] > 2:
            context += CPS_IMPROVING
        elif cp['cps_trend'] < -2:
            context += CPS_DECLINING
        
        context += "\n"
        return context
    
    def _build_match_context(self, m: Dict[str, Any]) -> str:
        """Build match context section"""
        context = MATCH_CONTEXT_HEADER
        context += MATCH_BASIC_INFO.format(
            game_type=m['game_type'],
            player_champion=m['player_champion']
        )
        
        # Add team compositions
        if m.get('your_team'):
            context += MATCH_YOUR_TEAM_HEADER
            for player in m['your_team']:
                context += MATCH_TEAM_PLAYER.format(
                    champion=player['champion'],
                    kills=player['kills'],
                    deaths=player['deaths'],
                    assists=player['assists']
                )
        
        if m.get('enemy_team'):
            context += MATCH_ENEMY_TEAM_HEADER
            for player in m['enemy_team']:
                context += MATCH_TEAM_PLAYER.format(
                    champion=player['champion'],
                    kills=player['kills'],
                    deaths=player['deaths'],
                    assists=player['assists']
                )
        
        # Add player's game stats
        if m.get('player_stats'):
            context += self._build_player_stats(m['player_stats'], m.get('game_duration', 0))
        
        # Add PRT (Power Ranking Timeline) data if available
        if m.get('analysis'):
            analysis = m['analysis']
            
            # Extract PRT data specifically
            if 'charts' in analysis and 'powerRankingTimeline' in analysis['charts']:
                prt_section = self._build_prt_analysis(analysis['charts']['powerRankingTimeline'], m['player_champion'])
                if prt_section:
                    context += prt_section
                    logger.info(f"✅ PRT data added to match context for {m['player_champion']}")
                else:
                    logger.warning(f"⚠️ PRT data exists but _build_prt_analysis returned empty for {m['player_champion']}")
            else:
                logger.warning(f"⚠️ No powerRankingTimeline found in analysis for match")
            
            # Extract CPS timeline data for all champions
            if 'charts' in analysis and 'powerScoreTimeline' in analysis['charts']:
                cps_section = self._build_cps_timeline_all_players(analysis['charts']['powerScoreTimeline'], m['player_champion'])
                if cps_section:
                    context += cps_section
                    logger.info(f"✅ CPS timeline data added to match context")
            
            # Add full analysis
            context += self._build_match_analysis(analysis, m['player_champion'])
        else:
            logger.warning(f"⚠️ No analysis data in match context")
        
        context += "\n"
        return context
    
    def _build_player_stats(self, stats: Dict[str, Any], game_duration: int) -> str:
        """Build player stats section"""
        stats_text = PLAYER_STATS_HEADER
        
        result = 'Victory' if stats['win'] else 'Defeat'
        stats_text += PLAYER_STATS_RESULT.format(result=result)
        
        # Handle None values
        kills = stats.get('kills', 0) or 0
        deaths = stats.get('deaths', 0) or 0
        assists = stats.get('assists', 0) or 0
        damage = stats.get('damage', 0) or 0
        gold = stats.get('gold', 0) or 0
        cs = stats.get('cs', 0) or 0
        
        stats_text += PLAYER_STATS_KDA.format(kills=kills, deaths=deaths, assists=assists)
        kda_ratio = (kills + assists) / max(deaths, 1)
        stats_text += PLAYER_STATS_KDA_RATIO.format(ratio=kda_ratio)
        stats_text += PLAYER_STATS_DAMAGE.format(damage=damage)
        stats_text += PLAYER_STATS_GOLD.format(gold=gold)
        stats_text += PLAYER_STATS_CS.format(cs=cs)
        stats_text += PLAYER_STATS_DURATION.format(duration=game_duration // 60)
        return stats_text
    
    def _build_match_analysis(self, analysis: Dict[str, Any], player_champ: str) -> str:
        """Build match analysis section"""
        analysis_text = "\n" + MATCH_ANALYSIS_HEADER
        
        # EPS Scores and Breakdown
        if 'rawStats' in analysis and 'epsScores' in analysis['rawStats']:
            analysis_text += self._build_eps_breakdown(analysis, player_champ)
        
        # CPS Scores (Cumulative Power Score from timeline)
        if 'charts' in analysis and 'powerScoreTimeline' in analysis['charts']:
            analysis_text += self._build_cps_timeline(analysis['charts']['powerScoreTimeline'], player_champ)
        
        analysis_text += HEIMERDINGER_ANALYSIS_INSTRUCTIONS
        
        return analysis_text
    
    def _build_eps_breakdown(self, analysis: Dict[str, Any], player_champ: str) -> str:
        """Build EPS breakdown section"""
        eps_scores = analysis['rawStats']['epsScores']
        
        breakdown_text = EPS_BREAKDOWN_HEADER
        if player_champ in eps_scores:
            player_eps = eps_scores[player_champ]
            breakdown_text += EPS_YOUR_SCORE.format(score=player_eps)
            
            # Rank among all 10 players
            sorted_scores = sorted(eps_scores.items(), key=lambda x: x[1], reverse=True)
            player_rank = next(i for i, (champ, _) in enumerate(sorted_scores, 1) if champ == player_champ)
            breakdown_text += EPS_YOUR_RANK.format(rank=player_rank)
            
            # Performance interpretation
            if player_eps >= 70:
                breakdown_text += EPS_LEVEL_EXCELLENT
            elif player_eps >= 50:
                breakdown_text += EPS_LEVEL_GOOD
            elif player_eps >= 30:
                breakdown_text += EPS_LEVEL_AVERAGE
            else:
                breakdown_text += EPS_LEVEL_NEEDS_IMPROVEMENT
            
            # EPS Breakdown from charts
            if 'charts' in analysis and 'epsBreakdown' in analysis['charts']:
                breakdown = analysis['charts']['epsBreakdown']
                datasets = breakdown.get('data', {}).get('datasets', [])
                labels = breakdown.get('data', {}).get('labels', [])
                
                if player_champ in labels:
                    champ_idx = labels.index(player_champ)
                    breakdown_text += EPS_BREAKDOWN_SECTION
                    for dataset in datasets:
                        score_type = dataset.get('label', 'Unknown')
                        scores = dataset.get('data', [])
                        if champ_idx < len(scores):
                            breakdown_text += EPS_BREAKDOWN_ITEM.format(
                                score_type=score_type,
                                score=scores[champ_idx]
                            )
            
            # Show top 3 performers for context
            breakdown_text += EPS_TOP_PERFORMERS_HEADER
            for i, (champ, score) in enumerate(sorted_scores[:3], 1):
                marker = " (YOU)" if champ == player_champ else ""
                breakdown_text += EPS_TOP_PERFORMER_ITEM.format(
                    rank=i,
                    champion=champ,
                    score=score,
                    marker=marker
                )
        
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
        
        cps_text = CPS_YOUR_SCORE_HEADER.format(score=player_cps)
        cps_text += CPS_DESCRIPTION.format(duration=game_duration_minutes)
        cps_text += CPS_EXPLANATION
        
        # Compare to other players
        all_final_scores = []
        for ds in datasets:
            scores = ds.get('data', [])
            if scores:
                all_final_scores.append((ds.get('label'), scores[-1]))
        
        all_final_scores.sort(key=lambda x: x[1], reverse=True)
        cps_rank = next(i for i, (champ, _) in enumerate(all_final_scores, 1) if champ == player_champ)
        cps_text += CPS_RANK.format(rank=cps_rank)
        
        return cps_text
    
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
    
    def _build_summoner_overview_context(self, overview: Dict[str, Any]) -> str:
        """Build summoner overview context section"""
        context = f"[PLAYER PROFILE]\n"
        context += f"Player: {overview['game_name']} | Region: {overview['region']}\n"
        
        # Handle None values
        level = overview.get('summoner_level', 0) or 0
        mastery = overview.get('total_mastery_score', 0) or 0
        champs_played = overview.get('total_champions_played', 0) or 0
        
        context += f"Level: {level} | Total Mastery: {mastery:,}\n"
        context += f"Champions Played: {champs_played}\n\n"
        
        # Top champions
        if overview.get('top_champions'):
            context += f"Top Champions (by Mastery):\n"
            for i, champ in enumerate(overview['top_champions'][:5], 1):
                champ_name = champ.get('championName', 'Unknown')
                points = champ.get('championPoints', 0) or 0
                level = champ.get('championLevel', 0) or 0
                context += f"  {i}. {champ_name} - Level {level} ({points:,} points)\n"
            context += "\n"
        
        return context
    
    def _build_champion_detailed_context(self, detailed: Dict[str, Any]) -> str:
        """Build detailed champion context section"""
        context = f"[CHAMPION DETAILED: {detailed['champion_name']}]\n"
        context += f"Total Games: {detailed['total_games']} | Win Rate: {detailed['win_rate']:.1f}%\n"
        
        # Handle None values for mastery
        mastery_level = detailed.get('mastery_level')
        mastery_points = detailed.get('mastery_points')
        if mastery_level is not None and mastery_points is not None:
            context += f"Mastery: Level {mastery_level} ({mastery_points:,} points)\n"
        elif mastery_level is not None:
            context += f"Mastery: Level {mastery_level}\n"
        else:
            context += f"Mastery: Not available\n"
        
        context += f"EPS Score: {detailed['avg_eps_score']:.1f}/100 (trend: {detailed['eps_trend']:+.1f} per game)\n"
        context += f"CPS Score: {detailed['avg_cps_score']:.1f}/1 (trend: {detailed['cps_trend']:+.1f} per game)\n"
        context += f"Average KDA: {detailed['avg_kda']:.2f}\n\n"
        
        # Best and worst games
        if detailed.get('best_game'):
            best = detailed['best_game']
            context += f"Best Game: {best.get('champion_name')} - EPS {best.get('eps_score', 0):.1f} "
            context += f"({best.get('kills', 0)}/{best.get('deaths', 0)}/{best.get('assists', 0)}) "
            context += f"{'Victory' if best.get('win') else 'Defeat'}\n"
        
        if detailed.get('worst_game'):
            worst = detailed['worst_game']
            context += f"Worst Game: {worst.get('champion_name')} - EPS {worst.get('eps_score', 0):.1f} "
            context += f"({worst.get('kills', 0)}/{worst.get('deaths', 0)}/{worst.get('assists', 0)}) "
            context += f"{'Victory' if worst.get('win') else 'Defeat'}\n"
        
        context += "\n"
        return context
    
    def _build_recent_performance_context(self, perf: Dict[str, Any]) -> str:
        """Build recent performance context section"""
        context = f"[RECENT PERFORMANCE - Last {perf['last_n_games']} Games]\n"
        context += f"Win Rate: {perf['overall_win_rate']:.1f}% ({perf['total_wins']}W - {perf['total_losses']}L)\n"
        context += f"Average KDA: {perf['avg_kda']:.2f}\n"
        context += f"Trend: {perf['recent_trend'].capitalize()}\n"
        
        # Current streak
        streak = perf.get('current_streak', {})
        if streak.get('count', 0) > 0:
            streak_type = streak.get('type', 'none').capitalize()
            context += f"Current Streak: {streak['count']} {streak_type}{'s' if streak['count'] > 1 else ''}\n"
        
        # Most played champions
        if perf.get('most_played_champions'):
            context += f"\nMost Played:\n"
            for champ_data in perf['most_played_champions'][:3]:
                context += f"  • {champ_data['champion']} ({champ_data['games']} games)\n"
        
        context += "\n"
        return context
    
    def _build_prt_analysis(self, prt_chart: Dict[str, Any], player_champ: str) -> str:
        """Build Power Ranking Timeline (PRT) analysis for detailed match context"""
        datasets = prt_chart.get('data', {}).get('datasets', [])
        
        if not datasets:
            logger.warning(f"No datasets in PRT chart")
            return ""
        
        # Find player's PRT dataset (labels include role like "Lux (UTILITY)")
        player_dataset = None
        for dataset in datasets:
            label = dataset.get('label', '')
            # Match either exact name or name with role (e.g., "Lux" matches "Lux (UTILITY)")
            if label == player_champ or label.startswith(f"{player_champ} ("):
                player_dataset = dataset
                logger.info(f"Matched PRT dataset: '{label}' for champion '{player_champ}'")
                break
        
        if not player_dataset:
            logger.warning(f"No PRT dataset found for {player_champ}. Available: {[d.get('label') for d in datasets]}")
            return ""
        
        prt_data = player_dataset.get('data', [])
        if not prt_data:
            logger.warning(f"PRT dataset for {player_champ} has no data")
            return ""
        
        if len(prt_data) < 3:
            logger.warning(f"PRT data too short for {player_champ}: {len(prt_data)} points (need at least 3)")
            return ""
        
        logger.info(f"Building PRT analysis for {player_champ} with {len(prt_data)} data points")
        
        prt_text = PRT_HEADER
        
        # Key game phases
        game_phases = []
        
        # Early game (first 5 minutes)
        if len(prt_data) > 5:
            early_avg = sum(prt_data[1:6]) / 5
            game_phases.append(("Early Game (0-5 min)", early_avg, prt_data[5]))
        
        # Mid game (10-15 minutes)
        if len(prt_data) > 15:
            mid_avg = sum(prt_data[10:16]) / 6
            game_phases.append(("Mid Game (10-15 min)", mid_avg, prt_data[15]))
        elif len(prt_data) > 10:
            mid_avg = sum(prt_data[10:min(16, len(prt_data))]) / (min(16, len(prt_data)) - 10)
            game_phases.append(("Mid Game (10+ min)", mid_avg, prt_data[min(15, len(prt_data)-1)]))
        
        # Late game (last 5 minutes)
        if len(prt_data) > 5:
            late_start = max(0, len(prt_data) - 5)
            late_avg = sum(prt_data[late_start:]) / (len(prt_data) - late_start)
            game_phases.append(("Late Game (final 5 min)", late_avg, prt_data[-1]))
        
        prt_text += PRT_GAME_PHASES_HEADER
        for phase_name, avg_power, final_power in game_phases:
            prt_text += f"  • {phase_name}: {final_power:.1f}% (avg: {avg_power:.1f}%)\n"
        
        # Trend analysis
        if len(prt_data) >= 10:
            first_half_avg = sum(prt_data[:len(prt_data)//2]) / (len(prt_data)//2)
            second_half_avg = sum(prt_data[len(prt_data)//2:]) / (len(prt_data) - len(prt_data)//2)
            
            prt_text += PRT_TREND_HEADER
            change = second_half_avg - first_half_avg
            if second_half_avg > first_half_avg + 10:
                prt_text += PRT_TREND_SCALING_UP.format(change=change)
            elif second_half_avg < first_half_avg - 10:
                prt_text += PRT_TREND_FALLING_OFF.format(change=change)
            else:
                prt_text += PRT_TREND_CONSISTENT
        
        # Analyze ALL players' PRT trends for comparison
        prt_text += PRT_ALL_PLAYERS_HEADER
        
        player_trends = []
        for dataset in datasets:
            champ_label = dataset.get('label', '')
            champ_data = dataset.get('data', [])
            
            if len(champ_data) >= 10:
                # Calculate trend
                first_half = sum(champ_data[:len(champ_data)//2]) / (len(champ_data)//2)
                second_half = sum(champ_data[len(champ_data)//2:]) / (len(champ_data) - len(champ_data)//2)
                trend_change = second_half - first_half
                
                # Get final power
                final_power = champ_data[-1]
                
                # Determine trend type
                if trend_change > 15:
                    trend_type = "↗ Scaled Hard"
                elif trend_change > 5:
                    trend_type = "↗ Scaled"
                elif trend_change < -15:
                    trend_type = "↘ Fell Off Hard"
                elif trend_change < -5:
                    trend_type = "↘ Fell Off"
                else:
                    trend_type = "→ Consistent"
                
                player_trends.append({
                    'label': champ_label,
                    'trend_change': trend_change,
                    'final_power': final_power,
                    'trend_type': trend_type,
                    'is_you': champ_label == player_champ or champ_label.startswith(f"{player_champ} (")
                })
        
        # Sort by final power
        player_trends.sort(key=lambda x: x['final_power'], reverse=True)
        
        # Show top 3 and bottom 2, plus player if not in those
        prt_text += PRT_TOP_PERFORMERS
        for i, trend in enumerate(player_trends[:3], 1):
            marker = " (YOU)" if trend['is_you'] else ""
            prt_text += f"  {i}. {trend['label']}: {trend['final_power']:.1f}% | {trend['trend_type']} ({trend['trend_change']:+.1f}%){marker}\n"
        
        prt_text += "\n" + PRT_BOTTOM_PERFORMERS
        for i, trend in enumerate(player_trends[-2:], 1):
            marker = " (YOU)" if trend['is_you'] else ""
            prt_text += f"  {i}. {trend['label']}: {trend['final_power']:.1f}% | {trend['trend_type']} ({trend['trend_change']:+.1f}%){marker}\n"
        
        # If player not in top 3 or bottom 2, show their position
        player_trend = next((t for t in player_trends if t['is_you']), None)
        if player_trend:
            player_rank = next((i+1 for i, t in enumerate(player_trends) if t['is_you']), None)
            if player_rank and player_rank > 3 and player_rank <= len(player_trends) - 2:
                prt_text += PRT_YOUR_POSITION.format(
                    rank=player_rank,
                    power=player_trend['final_power'],
                    trend=player_trend['trend_type'],
                    change=player_trend['trend_change']
                )
        
        prt_text += "\n"
        return prt_text
    
    def _build_cps_timeline_all_players(self, cps_chart: Dict[str, Any], player_champ: str) -> str:
        """Build CPS (Cumulative Power Score) timeline for all players"""
        datasets = cps_chart.get('data', {}).get('datasets', [])
        
        if not datasets:
            logger.warning(f"No datasets in CPS chart")
            return ""
        
        cps_text = CPS_TIMELINE_HEADER
        
        # Analyze all players' CPS
        player_cps_data = []
        for dataset in datasets:
            champ_label = dataset.get('label', '')
            cps_data = dataset.get('data', [])
            
            if len(cps_data) >= 3:
                # Get key CPS values
                final_cps = cps_data[-1] if cps_data else 0
                game_duration = len(cps_data) - 1
                avg_cps = final_cps / game_duration if game_duration > 0 else 0
                
                # Calculate growth rate (early vs late)
                if len(cps_data) > 10:
                    early_cps = cps_data[5] if len(cps_data) > 5 else 0
                    mid_cps = cps_data[len(cps_data)//2]
                    late_cps = final_cps
                    
                    # Growth pattern
                    early_rate = early_cps / 5 if early_cps > 0 else 0
                    late_rate = (late_cps - mid_cps) / (game_duration - len(cps_data)//2) if game_duration > len(cps_data)//2 else 0
                    
                    if late_rate > early_rate * 1.5:
                        growth_pattern = "↗ Accelerating"
                    elif late_rate < early_rate * 0.5:
                        growth_pattern = "↘ Slowing"
                    else:
                        growth_pattern = "→ Linear"
                else:
                    growth_pattern = "→ Consistent"
                
                player_cps_data.append({
                    'label': champ_label,
                    'final_cps': final_cps,
                    'avg_cps': avg_cps,
                    'growth_pattern': growth_pattern,
                    'is_you': champ_label == player_champ or champ_label.startswith(f"{player_champ} (")
                })
        
        # Sort by average CPS (overall strength)
        player_cps_data.sort(key=lambda x: x['avg_cps'], reverse=True)
        
        cps_text += CPS_ALL_PLAYERS_HEADER
        for i, data in enumerate(player_cps_data, 1):
            marker = " (YOU)" if data['is_you'] else ""
            cps_text += f"  {i}. {data['label']}: Avg CPS {data['avg_cps']:.1f} | Final {data['final_cps']:.1f} | {data['growth_pattern']}{marker}\n"
        
        # Highlight player's position
        player_data = next((d for d in player_cps_data if d['is_you']), None)
        if player_data:
            player_rank = next((i+1 for i, d in enumerate(player_cps_data) if d['is_you']), None)
            cps_text += CPS_YOUR_ANALYSIS_HEADER
            cps_text += CPS_YOUR_RANK.format(rank=player_rank)
            cps_text += CPS_YOUR_AVG.format(avg=player_data['avg_cps'])
            cps_text += CPS_YOUR_FINAL.format(final=player_data['final_cps'])
            cps_text += CPS_YOUR_GROWTH.format(growth=player_data['growth_pattern'])
        
        cps_text += "\n"
        return cps_text
