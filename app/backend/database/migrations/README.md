# Database Migrations

This folder contains SQL migration files for the Rift Rewind database.

## Running Migrations

### Option 1: Supabase Dashboard (Recommended)
1. Go to your Supabase project dashboard
2. Navigate to **SQL Editor**
3. Copy and paste the migration file contents
4. Click **Run** to execute

### Option 2: Supabase CLI
```bash
# Run the matches table migration
supabase db execute --file database/migrations/004_create_matches_table.sql
```

### Option 3: psql Command Line
```bash
psql -h <your-db-host> -U postgres -d postgres -f database/migrations/004_create_matches_table.sql
```

## Migration Files

### 004_create_matches_table.sql
Creates the `matches` table to store complete match data from Riot API.

**Key Features:**
- `match_id` (TEXT) as primary key - unique identifier from Riot API
- Basic match metadata (game_creation, game_duration, game_mode, etc.)
- `match_data` (JSONB) - stores complete match response for flexibility
- Indexes for efficient querying by date, queue, mode, platform
- GIN index on JSONB for fast JSON queries
- Row Level Security policies

**Table Structure:**
```sql
matches (
    match_id TEXT PRIMARY KEY,
    game_creation BIGINT NOT NULL,
    game_duration INTEGER NOT NULL,
    game_end_timestamp BIGINT,
    game_mode TEXT NOT NULL,
    game_type TEXT NOT NULL,
    game_version TEXT NOT NULL,
    map_id INTEGER NOT NULL,
    platform_id TEXT NOT NULL,
    queue_id INTEGER NOT NULL,
    tournament_code TEXT,
    match_data JSONB NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
)
```

## Example Queries

### Get all matches for a player (using JSONB)
```sql
SELECT m.* 
FROM matches m
WHERE m.match_data->'metadata'->'participants' @> '["player-puuid"]'::jsonb
ORDER BY m.game_creation DESC;
```

### Get player's recent matches with their stats
```sql
SELECT 
    m.match_id,
    m.game_creation,
    m.game_duration,
    m.game_mode,
    p.value->>'championName' as champion,
    (p.value->>'kills')::int as kills,
    (p.value->>'deaths')::int as deaths,
    (p.value->>'assists')::int as assists,
    (p.value->>'win')::boolean as win
FROM matches m,
    jsonb_array_elements(m.match_data->'info'->'participants') as p
WHERE p.value->>'puuid' = 'player-puuid'
ORDER BY m.game_creation DESC
LIMIT 20;
```

### Get player's champion statistics
```sql
SELECT 
    p.value->>'championName' as champion,
    COUNT(*) as games_played,
    SUM(CASE WHEN (p.value->>'win')::boolean THEN 1 ELSE 0 END) as wins,
    AVG((p.value->>'kills')::int) as avg_kills,
    AVG((p.value->>'deaths')::int) as avg_deaths,
    AVG((p.value->>'assists')::int) as avg_assists
FROM matches m,
    jsonb_array_elements(m.match_data->'info'->'participants') as p
WHERE p.value->>'puuid' = 'player-puuid'
GROUP BY p.value->>'championName'
ORDER BY games_played DESC;
```

### Check if a match already exists
```sql
SELECT EXISTS(SELECT 1 FROM matches WHERE match_id = 'NA1_1234567890');
```

## Notes

- The `matches` table uses Row Level Security (RLS) for data protection
- The `update_updated_at_column()` function must exist before running migrations
- Service role has full access to all data
- Users can only read matches they participated in
- JSONB column allows flexible storage of complete API responses
- GIN index enables efficient JSON querying
- Match data is stored once per match (no duplication)
