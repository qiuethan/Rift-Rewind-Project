"""
CPS (Cumulative Power Score) timeline prompts
"""

CPS_TIMELINE_HEADER = """
[CPS TIMELINE - All Players]
CPS = Cumulative Power Score. Shows power accumulation over time.
Higher CPS = Stronger power curve and better itemization/scaling.
Average CPS = Total CPS / Game Duration = Overall strength.

"""

CPS_ALL_PLAYERS_HEADER = "All Players' CPS Performance (sorted by average CPS):\n"

CPS_YOUR_ANALYSIS_HEADER = "\nYour CPS Analysis:\n"
CPS_YOUR_RANK = "  • Rank: #{rank}/10 in average CPS\n"
CPS_YOUR_AVG = "  • Average CPS: {avg:.1f} (overall strength throughout game)\n"
CPS_YOUR_FINAL = "  • Final CPS: {final:.1f} (total power accumulated)\n"
CPS_YOUR_GROWTH = "  • Growth: {growth}\n"
