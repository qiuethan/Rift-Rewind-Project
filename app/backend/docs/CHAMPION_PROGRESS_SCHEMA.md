# Champion Progress Database Schema

## Table: `champion_progress`

Tracks user progress and statistics for each champion they play.

### Schema

```sql
CREATE TABLE champion_progress (
    -- Primary Keys
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    
    -- Foreign Keys
    user_id UUID NOT NULL REFERENCES auth.users(id) ON DELETE CASCADE,
    puuid TEXT NOT NULL,
    
    -- Champion Info
    champion_id INTEGER NOT NULL,
    champion_name TEXT NOT NULL,
    
    -- Aggregate Statistics
    total_games INTEGER NOT NULL DEFAULT 0,
    wins INTEGER NOT NULL DEFAULT 0,
    losses INTEGER NOT NULL DEFAULT 0,
    win_rate DECIMAL(5,2) NOT NULL DEFAULT 0.00,
    
    -- Performance Averages
    avg_eps_score DECIMAL(6,2) NOT NULL DEFAULT 0.00,
    avg_cps_score DECIMAL(6,2) NOT NULL DEFAULT 0.00,
    avg_kda DECIMAL(6,2) NOT NULL DEFAULT 0.00,
    
    -- Trend Analysis
    recent_trend TEXT NOT NULL DEFAULT 'stable' CHECK (recent_trend IN ('improving', 'declining', 'stable')),
    last_played BIGINT NOT NULL, -- Unix timestamp
    
    -- Detailed History (JSONB)
    recent_matches JSONB DEFAULT '[]'::jsonb,
    performance_history JSONB DEFAULT '[]'::jsonb,
    
    -- Mastery Data (Optional)
    mastery_level INTEGER,
    mastery_points INTEGER,
    
    -- Timestamps
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),
    
    -- Constraints
    UNIQUE(user_id, champion_id)
);

-- Indexes for performance
CREATE INDEX idx_champion_progress_user_id ON champion_progress(user_id);
CREATE INDEX idx_champion_progress_champion_id ON champion_progress(champion_id);
CREATE INDEX idx_champion_progress_last_played ON champion_progress(last_played DESC);
CREATE INDEX idx_champion_progress_total_games ON champion_progress(total_games DESC);
CREATE INDEX idx_champion_progress_avg_eps ON champion_progress(avg_eps_score DESC);

-- Updated_at trigger
CREATE OR REPLACE FUNCTION update_champion_progress_updated_at()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER champion_progress_updated_at
    BEFORE UPDATE ON champion_progress
    FOR EACH ROW
    EXECUTE FUNCTION update_champion_progress_updated_at();
```

### Field Descriptions

| Field | Type | Description |
|-------|------|-------------|
| `id` | UUID | Primary key |
| `user_id` | UUID | Reference to auth.users table |
| `puuid` | TEXT | Player UUID from Riot API |
| `champion_id` | INTEGER | Champion ID from Riot API |
| `champion_name` | TEXT | Champion name (e.g., "Ahri", "Yasuo") |
| `total_games` | INTEGER | Total games played with this champion |
| `wins` | INTEGER | Number of wins |
| `losses` | INTEGER | Number of losses |
| `win_rate` | DECIMAL | Win rate percentage (0-100) |
| `avg_eps_score` | DECIMAL | Average End-game Performance Score |
| `avg_cps_score` | DECIMAL | Average final Cumulative Power Score |
| `avg_kda` | DECIMAL | Average KDA ratio |
| `recent_trend` | TEXT | Performance trend: 'improving', 'declining', or 'stable' |
| `last_played` | BIGINT | Unix timestamp of last game |
| `recent_matches` | JSONB | Array of last 50 match summaries |
| `performance_history` | JSONB | Array of last 100 performance data points |
| `mastery_level` | INTEGER | Champion mastery level (optional) |
| `mastery_points` | INTEGER | Champion mastery points (optional) |
| `created_at` | TIMESTAMPTZ | Record creation timestamp |
| `updated_at` | TIMESTAMPTZ | Last update timestamp |

### JSONB Structure

#### `recent_matches` Array
Each element contains:
```json
{
    "match_id": "NA1_1234567890",
    "champion_id": 103,
    "champion_name": "Ahri",
    "game_date": 1699564800,
    "eps_score": 85.5,
    "cps_score": 1250.3,
    "kda": 4.5,
    "win": true,
    "kills": 12,
    "deaths": 3,
    "assists": 15,
    "cs": 245,
    "gold": 15000,
    "damage": 25000,
    "vision_score": 45
}
```

#### `performance_history` Array
Each element contains:
```json
{
    "date": 1699564800,
    "eps_score": 85.5,
    "cps_score": 1250.3
}
```

### Relationships

```
auth.users (1) ----< (N) champion_progress
    |
    └─ user_id
```

### Usage Examples

#### Insert New Progress Record
```sql
INSERT INTO champion_progress (
    user_id, puuid, champion_id, champion_name,
    total_games, wins, losses, win_rate,
    avg_eps_score, avg_cps_score, avg_kda,
    recent_trend, last_played, recent_matches
) VALUES (
    'user-uuid-here',
    'player-puuid-here',
    103,
    'Ahri',
    1,
    1,
    0,
    100.00,
    85.50,
    1250.30,
    4.50,
    'stable',
    1699564800,
    '[{"match_id": "NA1_123", "eps_score": 85.5, ...}]'::jsonb
);
```

#### Update After Match
```sql
UPDATE champion_progress
SET 
    total_games = total_games + 1,
    wins = wins + CASE WHEN $win THEN 1 ELSE 0 END,
    losses = losses + CASE WHEN $win THEN 0 ELSE 1 END,
    win_rate = ((wins + CASE WHEN $win THEN 1 ELSE 0 END)::DECIMAL / (total_games + 1)) * 100,
    avg_eps_score = ((avg_eps_score * total_games) + $new_eps) / (total_games + 1),
    avg_cps_score = ((avg_cps_score * total_games) + $new_cps) / (total_games + 1),
    avg_kda = ((avg_kda * total_games) + $new_kda) / (total_games + 1),
    last_played = $game_date,
    recent_matches = jsonb_insert(recent_matches, '{0}', $new_match_json),
    recent_trend = $calculated_trend
WHERE user_id = $user_id AND champion_id = $champion_id;
```

#### Query Top Performing Champions
```sql
SELECT 
    champion_name,
    total_games,
    win_rate,
    avg_eps_score,
    recent_trend
FROM champion_progress
WHERE user_id = $user_id
ORDER BY avg_eps_score DESC
LIMIT 10;
```

#### Query Most Played Champions
```sql
SELECT 
    champion_name,
    total_games,
    win_rate,
    avg_eps_score
FROM champion_progress
WHERE user_id = $user_id
ORDER BY total_games DESC
LIMIT 10;
```

### Row-Level Security (RLS)

```sql
-- Enable RLS
ALTER TABLE champion_progress ENABLE ROW LEVEL SECURITY;

-- Users can only see their own progress
CREATE POLICY "Users can view own champion progress"
    ON champion_progress
    FOR SELECT
    USING (auth.uid() = user_id);

-- Users can only insert their own progress
CREATE POLICY "Users can insert own champion progress"
    ON champion_progress
    FOR INSERT
    WITH CHECK (auth.uid() = user_id);

-- Users can only update their own progress
CREATE POLICY "Users can update own champion progress"
    ON champion_progress
    FOR UPDATE
    USING (auth.uid() = user_id);

-- Users can only delete their own progress
CREATE POLICY "Users can delete own champion progress"
    ON champion_progress
    FOR DELETE
    USING (auth.uid() = user_id);
```

### Migration Script

To create this table in your Supabase database, run the SQL commands above in the Supabase SQL Editor.

### Notes

- The `recent_matches` array is limited to 50 matches to prevent excessive storage
- The `performance_history` array is limited to 100 data points
- Trend calculation compares recent performance (last 5 games) to previous performance
- All scores are stored with 2 decimal precision for consistency
- The unique constraint on `(user_id, champion_id)` ensures one record per user per champion
- Indexes are optimized for common query patterns (by user, by champion, by performance)
