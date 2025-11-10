"""
PRT (Power Ranking Timeline) analysis prompts
"""

PRT_HEADER = """
[POWER RANKING TIMELINE (PRT)]
IMPORTANT: PRT at each minute shows your INSTANTANEOUS power level at that specific moment.
It's like a snapshot - how strong you were RIGHT THEN, not cumulative.
To assess overall strength, look at AVERAGE PRT across the entire game.

Understanding PRT values:
- Higher % = You were stronger than more players at that moment
- 0% = You performed the worst out of all 10 players that minute (often means you died)
- PRT measures relative performance, not absolute strength

"""

PRT_GAME_PHASES_HEADER = "Your Power Level by Game Phase:\n"

PRT_TREND_HEADER = "\nPower Trend:\n"

PRT_TREND_SCALING_UP = "  ↗ Scaling Up: You got stronger as the game progressed ({change:+.1f}%)\n"
PRT_TREND_FALLING_OFF = "  ↘ Falling Off: You lost power advantage as game went on ({change:+.1f}%)\n"
PRT_TREND_CONSISTENT = "  → Consistent: Your power level stayed relatively stable\n"

PRT_ALL_PLAYERS_HEADER = "\nAll Players' Power Trends (for context):\n"
PRT_TOP_PERFORMERS = "Top Performers (by end-game power):\n"
PRT_BOTTOM_PERFORMERS = "\nBottom Performers:\n"
PRT_YOUR_POSITION = "\nYour Position: #{rank}/10 | {power:.1f}% | {trend} ({change:+.1f}%)\n"
