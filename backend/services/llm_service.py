"""
AWS Bedrock LLM Service
Handles interactions with AWS Bedrock for AI-powered analytics
"""
import json
import boto3
from typing import Optional, Dict, Any
from config.settings import settings


class BedrockService:
    """Service for interacting with AWS Bedrock LLMs"""
    
    def __init__(self):
        """Initialize Bedrock client"""
        self.client = None
        self._initialize_client()
    
    def _initialize_client(self):
        """Initialize boto3 Bedrock client with credentials"""
        if not settings.AWS_ACCESS_KEY_ID or not settings.AWS_SECRET_ACCESS_KEY:
            print("⚠️  Warning: AWS credentials not configured")
            return
        
        try:
            self.client = boto3.client(
                service_name='bedrock-runtime',
                region_name=settings.AWS_REGION,
                aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
                aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY
            )
            print(f"✅ AWS Bedrock client initialized (region: {settings.AWS_REGION})")
        except Exception as e:
            print(f"❌ Failed to initialize AWS Bedrock client: {e}")
            self.client = None
    
    async def generate_match_analysis(
        self,
        match_data: Dict[str, Any],
        player_puuid: str
    ) -> Optional[str]:
        """
        Generate AI-powered match analysis using AWS Bedrock
        
        Args:
            match_data: Complete match data from Riot API
            player_puuid: PUUID of the player to analyze
            
        Returns:
            AI-generated analysis text or None if failed
        """
        if not self.client:
            return "AI analysis unavailable: AWS Bedrock not configured"
        
        try:
            # Extract relevant player data
            player_stats = self._extract_player_stats(match_data, player_puuid)
            
            # Build prompt
            prompt = self._build_analysis_prompt(player_stats)
            
            # Call Bedrock
            response = await self._invoke_bedrock(prompt)
            
            return response
        
        except Exception as e:
            logger.error(f"Error generating match analysis: {e}")
            return f"Error generating analysis: {str(e)}"
    
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
            'win': player_data.get('win', False),
            'items': [
                player_data.get(f'item{i}', 0)
                for i in range(7)
                if player_data.get(f'item{i}', 0) != 0
            ]
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
    
    async def _invoke_bedrock(self, prompt: str) -> str:
        """
        Invoke AWS Bedrock with the given prompt
        
        Args:
            prompt: The prompt to send to the model
            
        Returns:
            Generated text response
        """
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
    
    async def generate_champion_recommendation(
        self,
        player_stats: Dict[str, Any],
        recent_matches: list
    ) -> Optional[str]:
        """
        Generate champion recommendations based on player history
        
        Args:
            player_stats: Player's overall statistics
            recent_matches: List of recent match data
            
        Returns:
            AI-generated recommendations or None if failed
        """
        if not self.client:
            return "AI recommendations unavailable: AWS Bedrock not configured"
        
        try:
            prompt = f"""Based on this League of Legends player's recent performance, suggest 3 champions they should try:

Recent matches played: {len(recent_matches)}
Most played roles: {', '.join(player_stats.get('top_roles', ['Unknown'])[:3])}
Average KDA: {player_stats.get('avg_kda', 0):.2f}
Win rate: {player_stats.get('win_rate', 0):.1f}%

Provide 3 champion recommendations with brief reasoning for each."""

            response = await self._invoke_bedrock(prompt)
            return response
        
        except Exception as e:
            logger.error(f"Error generating recommendations: {e}")
            return f"Error generating recommendations: {str(e)}"


# Global service instance
bedrock_service = BedrockService()
