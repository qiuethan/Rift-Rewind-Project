"""
Repository-level constants for database and API operations
"""

# Database connection pool limits
# Supabase typically has 15-25 connection limit on free tier
MAX_CONCURRENT_DB_READS = 3  # Max concurrent DB read operations
MAX_CONCURRENT_DB_WRITES = 1  # Max concurrent DB write operations (sequential for safety)

# Match syncing limits
DEFAULT_INITIAL_MATCH_COUNT = 10  # Number of matches to fetch on account link
MAX_BACKGROUND_SYNC_MATCHES = 100  # Maximum matches to sync in background

# Cache settings
DEFAULT_CACHED_GAMES_COUNT = 100  # Number of games to cache in summoners.recent_games

# Retry settings for database operations
DB_RETRY_MAX_ATTEMPTS = 5  # Maximum retry attempts for DB operations
DB_RETRY_INITIAL_DELAY = 1.0  # Initial retry delay in seconds (exponential backoff)
DB_OPERATION_DELAY = 0.1  # Delay between sequential DB operations (seconds)
