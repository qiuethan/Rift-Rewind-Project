"""
Metric definition prompts for EPS, CPS, PRT
"""

METRIC_DEFINITIONS = """[METRIC DEFINITIONS]
- EPS (End-Game Performance Score): Overall match performance - SKILL
  * Score range: 0-100 (always out of 100)
  * Measures how well the PLAYER performed in the match
  * Combat (40%): KDA, damage dealt, damage taken
  * Economic (30%): Gold earned, CS, gold efficiency
  * Objective (30%): Turret damage, objective participation
  * EPS trending up = Skill improving | EPS trending down = Skill declining
- CPS (Cumulative Power Score): Champion power/itemization - BUILD
  * Score range: 0 to game_duration_in_minutes (scales with game length)
  * Measures champion's accumulated power and strength during the match
  * Economic (45%): Gold and experience advantages
  * Offensive (35%): Damage output and kills
  * Defensive (20%): Survivability and damage mitigation
- PRT (Power Ranking Timeline): Relative strength over time - GAME FLOW
  * Score range: 0-100 at each minute (percentile ranking)
  * Tracks how strong you were compared to all 10 players throughout the game
  * Higher % = You were stronger than more players at that moment
  * Shows early/mid/late game performance and scaling patterns
  * Use to identify power spikes, weak phases, and whether you scaled well
  * CPS trending up = Building correctly/ahead | CPS trending down = Behind in building or building incorrectly
- Trend: Percentage change per game (positive = improving, negative = declining)

"""

MATCH_ANALYSIS_HEADER = """[PERFORMANCE METRICS - ALL 10 PLAYERS]
EPS (End-Game Performance Score): Measures SKILL - how well you played
  • Combat (40%): KDA, damage dealt, damage taken
  • Economic (30%): Gold earned, CS, gold efficiency
  • Objective (30%): Turret damage, objective participation
  • Score range: 0-100 (higher is better)

CPS (Champion Performance Score): Measures CHAMPION EFFECTIVENESS
  • How well the champion performed relative to its potential
  • Considers itemization, build efficiency, champion-specific metrics
  • Score range: 0-1 (higher is better, normally distributed)

"""
