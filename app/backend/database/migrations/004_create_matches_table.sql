-- ============================================
-- Migration: Create matches table
-- Description: Store all match data from Riot API with match_id as primary key
-- ============================================

-- Create matches table
CREATE TABLE IF NOT EXISTS public.matches (
    match_id TEXT PRIMARY KEY,
    
    -- Basic match info
    game_creation BIGINT NOT NULL,  -- Unix timestamp in milliseconds
    game_duration INTEGER NOT NULL,  -- Duration in seconds
    game_end_timestamp BIGINT,  -- Unix timestamp in milliseconds
    game_mode TEXT NOT NULL,  -- e.g., "CLASSIC", "ARAM"
    game_type TEXT NOT NULL,  -- e.g., "MATCHED_GAME"
    game_version TEXT NOT NULL,  -- Patch version
    map_id INTEGER NOT NULL,  -- Map ID (11 = Summoner's Rift)
    platform_id TEXT NOT NULL,  -- e.g., "NA1", "EUW1"
    queue_id INTEGER NOT NULL,  -- Queue type ID
    tournament_code TEXT,  -- Optional tournament code
    
    -- Store complete match data as JSONB for flexibility
    match_data JSONB NOT NULL,
    
    -- Metadata
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Create indexes for efficient querying
CREATE INDEX IF NOT EXISTS idx_matches_game_creation ON public.matches(game_creation DESC);
CREATE INDEX IF NOT EXISTS idx_matches_queue_id ON public.matches(queue_id);
CREATE INDEX IF NOT EXISTS idx_matches_game_mode ON public.matches(game_mode);
CREATE INDEX IF NOT EXISTS idx_matches_platform_id ON public.matches(platform_id);

-- Create GIN index for JSONB data (allows efficient querying of match_data)
CREATE INDEX IF NOT EXISTS idx_matches_match_data ON public.matches USING GIN (match_data);

-- Enable Row Level Security
ALTER TABLE public.matches ENABLE ROW LEVEL SECURITY;

-- Create trigger to automatically update updated_at
CREATE TRIGGER update_matches_updated_at
    BEFORE UPDATE ON public.matches
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

-- ============================================
-- Row Level Security Policies
-- ============================================

-- Allow service role to manage all matches
CREATE POLICY "Service role can manage all matches"
    ON public.matches
    FOR ALL
    USING (auth.role() = 'service_role');

-- Allow users to read matches they participated in
-- (This requires checking if their PUUID is in the match_data JSONB)
CREATE POLICY "Users can read their own matches"
    ON public.matches
    FOR SELECT
    USING (
        EXISTS (
            SELECT 1 FROM public.user_summoners us
            WHERE us.user_id = auth.uid()
            AND match_data->'info'->'participants' @> jsonb_build_array(
                jsonb_build_object('puuid', us.puuid)
            )
        )
    );

-- ============================================
-- Migration Complete!
-- ============================================
