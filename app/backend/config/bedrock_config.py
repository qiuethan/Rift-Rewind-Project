"""
AWS Bedrock Configuration
Defines models and prompt routing configuration
"""

# Bedrock Model Configuration
class BedrockModels:
    """Available Bedrock models with inference profiles"""
    
    # Claude Haiku 4.5 - Fast and efficient for simple tasks (routing/classification)
    CLAUDE_HAIKU_4_5 = "us.anthropic.claude-haiku-4-5-20251001-v1:0"
    CLAUDE_HAIKU_4 = CLAUDE_HAIKU_4_5  # Alias
    
    # Claude Sonnet 4.5 - Best for all other tasks (main responses)
    CLAUDE_SONNET_4_5 = "us.anthropic.claude-sonnet-4-5-20250929-v1:0"
    CLAUDE_SONNET_4 = CLAUDE_SONNET_4_5  # Alias


# Prompt Router Configuration
class PromptRouterConfig:
    """Configuration for AWS Bedrock Prompt Router"""
    
    # Router model - determines which model to use based on prompt complexity
    ROUTER_MODEL = BedrockModels.CLAUDE_HAIKU_4_5
    
    # Model routing rules based on task complexity
    ROUTING_RULES = {
        "simple": {
            "model": BedrockModels.CLAUDE_HAIKU_4_5,
            "max_tokens": 500,
            "temperature": 0.5,
            "description": "Fast responses for simple queries (greetings, basic info, quick lookups)"
        },
        "moderate": {
            "model": BedrockModels.CLAUDE_SONNET_4_5,
            "max_tokens": 2000,
            "temperature": 0.7,
            "description": "Balanced for most tasks (match analysis, summaries, recommendations)"
        },
        "complex": {
            "model": BedrockModels.CLAUDE_SONNET_4_5,
            "max_tokens": 4000,
            "temperature": 0.8,
            "description": "Deep analysis for complex reasoning (strategy, predictions, coaching)"
        }
    }
    
    # Default model if routing fails
    DEFAULT_MODEL = BedrockModels.CLAUDE_SONNET_4_5
    DEFAULT_MAX_TOKENS = 1500
    DEFAULT_TEMPERATURE = 0.7
    DEFAULT_TOP_P = 0.9


# Task Classification Prompts
class RouterPrompts:
    """Prompts for classifying task complexity and context needs"""
    
    CLASSIFICATION_PROMPT = """Analyze this user request and classify its complexity level.

User Request: {user_prompt}

Classify as one of:
- "simple": Basic questions, greetings, simple facts, quick lookups (e.g., "What is KDA?", "Hello", "Who is Yasuo?")
- "moderate": Standard analysis, summaries, explanations, recommendations (e.g., "Analyze this match", "Explain champion strengths", "Suggest a build")
- "complex": Deep strategic analysis, predictions, multi-step reasoning, coaching (e.g., "Predict team comp counters", "Analyze meta trends", "Create a training plan")

Respond with ONLY the classification word (simple/moderate/complex)."""
    
    CONTEXT_ROUTING_PROMPT = """You are a routing assistant for Rift Rewind, a League of Legends analytics platform.

Your role: Analyze user questions and determine what data needs to be fetched from the database.

User Request: {user_prompt}

Available data contexts:
1. "summoner" - Basic player info (game_name, region) - ALWAYS include this
2. {{"champion_progress": "ChampionName"}} - Champion-specific stats (games played, win rate, performance trends)
3. {{"match": "match_id"}} - Specific match data (KDA, items, timeline)

Instructions:
- Always include "summoner" as the first context
- Add champion_progress if the user mentions a specific champion by name
- Add match if the user wants to discuss a specific game/match
- Extract the exact champion name from the user's question
- Use "match_id" as placeholder for match context

Examples:
User: "How am I doing overall?" → {{"contexts": ["summoner"]}}
User: "How am I doing on Yasuo?" → {{"contexts": ["summoner", {{"champion_progress": "Yasuo"}}]}}
User: "Analyze my last match" → {{"contexts": ["summoner", {{"match": "match_id"}}]}}
User: "How did I play Ahri in my last game?" → {{"contexts": ["summoner", {{"champion_progress": "Ahri"}}, {{"match": "match_id"}}]}}

Respond with ONLY the JSON object, no markdown, no explanation:"""


# Use Cases for Rift Rewind
class RiftRewindUseCases:
    """Common use cases and their recommended models"""
    
    USE_CASE_ROUTING = {
        # Simple tasks - Use Haiku (fast & cheap)
        "greeting": "simple",
        "basic_info": "simple",
        "champion_lookup": "simple",
        "item_lookup": "simple",
        "ability_info": "simple",
        
        # Moderate tasks - Use Sonnet 3.5
        "match_summary": "moderate",
        "player_analysis": "moderate",
        "champion_tips": "moderate",
        "build_recommendation": "moderate",
        "performance_feedback": "moderate",
        "rune_suggestion": "moderate",
        "lane_matchup": "moderate",
        
        # Complex tasks - Use Sonnet 4.1
        "team_comp_analysis": "complex",
        "meta_prediction": "complex",
        "strategic_planning": "complex",
        "multi_match_trends": "complex",
        "coaching_advice": "complex",
        "win_condition_analysis": "complex",
        "draft_strategy": "complex"
    }
