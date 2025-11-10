"""
EPS (End-Game Performance Score) analysis prompts
"""

EPS_BREAKDOWN_HEADER = "[YOUR PERFORMANCE]\n"
EPS_YOUR_SCORE = "Your EPS Score: {score:.1f}/100\n"
EPS_YOUR_RANK = "Your Rank: #{rank} out of 10 players (both teams)\n"

# Performance level indicators
EPS_LEVEL_EXCELLENT = "Performance Level: Excellent! 🌟\n"
EPS_LEVEL_GOOD = "Performance Level: Good ✓\n"
EPS_LEVEL_AVERAGE = "Performance Level: Average\n"
EPS_LEVEL_NEEDS_IMPROVEMENT = "Performance Level: Needs improvement\n"

# Breakdown section
EPS_BREAKDOWN_SECTION = "\nYour Score Breakdown:\n"
EPS_BREAKDOWN_ITEM = "  • {score_type}: {score:.1f}\n"

# Top performers
EPS_TOP_PERFORMERS_HEADER = "\nTop 3 EPS Performers:\n"
EPS_TOP_PERFORMER_ITEM = "  {rank}. {champion}: {score:.1f}{marker}\n"

# CPS timeline (old single-player version)
CPS_YOUR_SCORE_HEADER = "\nYour CPS (Cumulative Power Score): {score:.1f}\n"
CPS_DESCRIPTION = "CPS measures your power accumulation over {duration} minutes.\n"
CPS_EXPLANATION = "Higher CPS = stronger power curve and game impact over time.\n"
CPS_RANK = "CPS Rank: #{rank} out of 10 players\n"
