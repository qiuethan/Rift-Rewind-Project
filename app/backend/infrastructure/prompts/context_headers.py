"""
Context section headers and basic formatting
"""

# Player context
PLAYER_CONTEXT_HEADER = "[PLAYER CONTEXT]\n"
PLAYER_INFO = "Player: {game_name} | Region: {region}\n\n"

# Player profile (overview)
PLAYER_PROFILE_HEADER = "[PLAYER PROFILE]\n"
PLAYER_PROFILE_INFO = "Player: {game_name} | Region: {region}\n"
PLAYER_PROFILE_LEVEL = "Level: {level} | Total Mastery: {mastery:,}\n"
PLAYER_PROFILE_CHAMPS = "Champions Played: {champs_played}\n\n"

# Champion stats
CHAMPION_STATS_HEADER = "[CHAMPION STATS: {champion_name}]\n"
CHAMPION_BASIC_STATS = "Total Games: {total_games} | Win Rate: {win_rate:.1f}%\n"
CHAMPION_EPS = "EPS Score: {eps:.1f}/100 (trend: {trend:+.1f} per game)\n"
CHAMPION_CPS = "CPS Score: {cps:.1f}/1 (normally distributed) (trend: {trend:+.1f} per game)\n"

# Trend indicators
EPS_IMPROVING = "📈 EPS improving significantly\n"
EPS_DECLINING = "📉 EPS declining - skill issue\n"
CPS_IMPROVING = "📈 CPS improving significantly\n"
CPS_DECLINING = "📉 CPS declining - itemization lacking/issue\n"

# Match context
MATCH_CONTEXT_HEADER = "[MATCH CONTEXT]\n"
MATCH_BASIC_INFO = "Game Type: {game_type} | Champion Played: {player_champion}\n"

# Team compositions
MATCH_YOUR_TEAM_HEADER = "\n[YOUR TEAM]\n"
MATCH_ENEMY_TEAM_HEADER = "\n[ENEMY TEAM]\n"
MATCH_TEAM_PLAYER = "  • {champion} ({kills}/{deaths}/{assists})\n"

# Player stats
PLAYER_STATS_HEADER = "\n[YOUR GAME STATS]\n"
PLAYER_STATS_RESULT = "Result: {result}\n"
PLAYER_STATS_KDA = "KDA: {kills}/{deaths}/{assists}\n"
PLAYER_STATS_KDA_RATIO = "KDA Ratio: {ratio:.2f}\n"
PLAYER_STATS_DAMAGE = "Damage to Champions: {damage:,}\n"
PLAYER_STATS_GOLD = "Gold Earned: {gold:,}\n"
PLAYER_STATS_CS = "CS: {cs}\n"
PLAYER_STATS_DURATION = "Game Duration: {duration} minutes\n"

# Champion detailed
CHAMPION_DETAILED_HEADER = "[CHAMPION DETAILED: {champion_name}]\n"
CHAMPION_DETAILED_GAMES = "Total Games: {total_games} | Win Rate: {win_rate:.1f}%\n"
CHAMPION_DETAILED_SCORES = "Average EPS: {eps:.1f}/100 | Average CPS: {cps:.1f}/1\n"
CHAMPION_DETAILED_MASTERY = "Mastery: Level {level} ({points:,} points)\n"
CHAMPION_DETAILED_MASTERY_NA = "Mastery: Not available\n"

# Match detailed
MATCH_DETAILED_HEADER = "[MATCH DETAILED]\n"
MATCH_DETAILED_INFO = "Game Mode: {game_mode} | Version: {version} | Queue: {queue}\n"
MATCH_DETAILED_DURATION = "Duration: {duration} minutes\n"

# Recent performance
RECENT_PERFORMANCE_HEADER = "[RECENT PERFORMANCE - Last {n} Games]\n"
RECENT_PERFORMANCE_WIN_RATE = "Win Rate: {win_rate:.1f}% ({wins}W - {losses}L)\n"
RECENT_PERFORMANCE_KDA = "Average KDA: {kda:.2f}\n"
RECENT_PERFORMANCE_TREND = "Trend: {trend}\n"
RECENT_PERFORMANCE_STREAK = "Current Streak: {count} {type}{'s' if count > 1 else ''}\n"
