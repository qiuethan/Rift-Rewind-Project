"""
Analytics domain - Pure business logic for analytics operations
"""
from fastapi import HTTPException, status
from typing import List, Dict


class AnalyticsDomain:
    """Pure business logic for analytics operations"""
    
    def __init__(self):
        pass
    
    def validate_time_range(self, days: int) -> None:
        """Validate time range for analytics"""
        if days < 1 or days > 365:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Time range must be between 1 and 365 days"
            )
    
    def validate_match_list(self, match_ids: List[str]) -> None:
        """Validate match ID list"""
        if not match_ids or len(match_ids) == 0:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="At least one match ID is required"
            )
        
        if len(match_ids) > 10:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Maximum 10 match IDs allowed"
            )
    
    def calculate_performance_grade(self, metrics: Dict[str, float]) -> str:
        """
        Calculate performance grade based on metrics
        Returns: S, A, B, C, D, or F
        """
        # Simple scoring system for demo
        score = 0
        
        # KDA scoring (0-30 points)
        kda = metrics.get('kda', 0)
        if kda >= 5:
            score += 30
        elif kda >= 3:
            score += 20
        elif kda >= 2:
            score += 10
        
        # CS/min scoring (0-25 points)
        cs_per_min = metrics.get('cs_per_min', 0)
        if cs_per_min >= 8:
            score += 25
        elif cs_per_min >= 6:
            score += 15
        elif cs_per_min >= 4:
            score += 5
        
        # Kill participation scoring (0-25 points)
        kill_participation = metrics.get('kill_participation', 0)
        if kill_participation >= 70:
            score += 25
        elif kill_participation >= 50:
            score += 15
        elif kill_participation >= 30:
            score += 5
        
        # Vision score scoring (0-20 points)
        vision_score = metrics.get('vision_score', 0)
        if vision_score >= 50:
            score += 20
        elif vision_score >= 30:
            score += 10
        elif vision_score >= 15:
            score += 5
        
        # Convert score to grade
        if score >= 90:
            return "S"
        elif score >= 75:
            return "A"
        elif score >= 60:
            return "B"
        elif score >= 45:
            return "C"
        elif score >= 30:
            return "D"
        else:
            return "F"
    
    def identify_strengths(self, metrics: Dict[str, float]) -> List[str]:
        """Identify player strengths based on metrics"""
        strengths = []
        
        if metrics.get('kda', 0) >= 3:
            strengths.append("Excellent KDA - Great at staying alive and contributing to kills")
        
        if metrics.get('cs_per_min', 0) >= 7:
            strengths.append("Strong farming - Consistently high CS per minute")
        
        if metrics.get('kill_participation', 0) >= 60:
            strengths.append("High kill participation - Active in team fights")
        
        if metrics.get('vision_score', 0) >= 40:
            strengths.append("Good vision control - Strong map awareness")
        
        if metrics.get('damage_per_min', 0) >= 600:
            strengths.append("High damage output - Effective in fights")
        
        return strengths if strengths else ["Consistent gameplay"]
    
    def identify_weaknesses(self, metrics: Dict[str, float]) -> List[str]:
        """Identify player weaknesses based on metrics"""
        weaknesses = []
        
        if metrics.get('kda', 0) < 2:
            weaknesses.append("Low KDA - Focus on reducing deaths and improving positioning")
        
        if metrics.get('cs_per_min', 0) < 5:
            weaknesses.append("Low CS - Work on last-hitting and farming patterns")
        
        if metrics.get('kill_participation', 0) < 40:
            weaknesses.append("Low kill participation - Be more present in team fights")
        
        if metrics.get('vision_score', 0) < 20:
            weaknesses.append("Low vision score - Place more wards and clear enemy vision")
        
        if metrics.get('gold_per_min', 0) < 300:
            weaknesses.append("Low gold income - Focus on farming and objective control")
        
        return weaknesses if weaknesses else ["Room for improvement in all areas"]
    
    def generate_recommendations(self, strengths: List[str], weaknesses: List[str]) -> List[str]:
        """Generate actionable recommendations"""
        recommendations = []
        
        if any("CS" in w for w in weaknesses):
            recommendations.append("Practice last-hitting in practice tool for 10 minutes daily")
        
        if any("KDA" in w for w in weaknesses):
            recommendations.append("Focus on positioning and map awareness to reduce deaths")
        
        if any("vision" in w.lower() for w in weaknesses):
            recommendations.append("Set a goal to place 1 ward per minute and clear 2-3 enemy wards per game")
        
        if any("participation" in w.lower() for w in weaknesses):
            recommendations.append("Improve map awareness and rotate to objectives earlier")
        
        if not recommendations:
            recommendations.append("Continue current gameplay and focus on consistency")
        
        return recommendations
    
    def extract_player_stats_from_match(
        self,
        match_data: Dict,
        player_puuid: str
    ) -> Dict[str, any]:
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
            'win': player_data.get('win', False),
            'items': [
                player_data.get(f'item{i}', 0)
                for i in range(7)
                if player_data.get(f'item{i}', 0) != 0
            ]
        }
    
    def build_match_analysis_prompt(self, stats: Dict[str, any]) -> str:
        """Build prompt for AI match analysis"""
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
    
    def build_champion_recommendation_prompt(
        self,
        player_stats: Dict[str, any],
        recent_matches: List
    ) -> str:
        """Build prompt for champion recommendations"""
        prompt = f"""Based on this League of Legends player's recent performance, suggest 3 champions they should try:

Recent matches played: {len(recent_matches)}
Most played roles: {', '.join(player_stats.get('top_roles', ['Unknown'])[:3])}
Average KDA: {player_stats.get('avg_kda', 0):.2f}
Win rate: {player_stats.get('win_rate', 0):.1f}%

Provide 3 champion recommendations with brief reasoning for each."""

        return prompt
