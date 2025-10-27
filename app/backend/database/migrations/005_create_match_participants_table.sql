-- ============================================
-- Migration: Create match_participants table
-- Description: Store individual participant data for efficient querying
-- ============================================

-- Create match_participants table
CREATE TABLE IF NOT EXISTS public.match_participants (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    match_id TEXT NOT NULL,
    puuid TEXT NOT NULL,
    participant_id INTEGER NOT NULL,  -- 1-10 in the match
    
    -- Champion info
    champion_id INTEGER NOT NULL,
    champion_name TEXT NOT NULL,
    
    -- Core stats
    kills INTEGER NOT NULL DEFAULT 0,
    deaths INTEGER NOT NULL DEFAULT 0,
    assists INTEGER NOT NULL DEFAULT 0,
    gold_earned INTEGER NOT NULL DEFAULT 0,
    total_damage_dealt_to_champions INTEGER NOT NULL DEFAULT 0,
    total_minions_killed INTEGER NOT NULL DEFAULT 0,
    neutral_minions_killed INTEGER NOT NULL DEFAULT 0,
    vision_score INTEGER NOT NULL DEFAULT 0,
    
    -- Position
    team_position TEXT,  -- TOP, JUNGLE, MIDDLE, BOTTOM, UTILITY
    individual_position TEXT,
    team_id INTEGER NOT NULL,  -- 100 (Blue) or 200 (Red)
    
    -- Result
    win BOOLEAN NOT NULL,
    
    -- Store complete participant data as JSONB
    participant_data JSONB NOT NULL,
    
    -- Metadata
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    
    -- Foreign key to matches table
    CONSTRAINT fk_match FOREIGN KEY (match_id) REFERENCES public.matches(match_id) ON DELETE CASCADE,
    
    -- Unique constraint: one record per participant per match
    CONSTRAINT unique_match_participant UNIQUE (match_id, puuid)
);

-- Create indexes for efficient querying
CREATE INDEX IF NOT EXISTS idx_match_participants_match_id ON public.match_participants(match_id);
CREATE INDEX IF NOT EXISTS idx_match_participants_puuid ON public.match_participants(puuid);
CREATE INDEX IF NOT EXISTS idx_match_participants_champion_id ON public.match_participants(champion_id);
CREATE INDEX IF NOT EXISTS idx_match_participants_win ON public.match_participants(win);
CREATE INDEX IF NOT EXISTS idx_match_participants_team_position ON public.match_participants(team_position);

-- Composite index for player's match history
CREATE INDEX IF NOT EXISTS idx_match_participants_puuid_match ON public.match_participants(puuid, match_id);

-- Create GIN index for JSONB data
CREATE INDEX IF NOT EXISTS idx_match_participants_data ON public.match_participants USING GIN (participant_data);

-- Enable Row Level Security
ALTER TABLE public.match_participants ENABLE ROW LEVEL SECURITY;

-- ============================================
-- Row Level Security Policies
-- ============================================

-- Allow service role to manage all participants
CREATE POLICY "Service role can manage all match participants"
    ON public.match_participants
    FOR ALL
    USING (auth.role() = 'service_role');

-- Allow users to read their own match participation
CREATE POLICY "Users can read their own match participation"
    ON public.match_participants
    FOR SELECT
    USING (
        puuid IN (
            SELECT puuid FROM public.user_summoners
            WHERE user_id = auth.uid()
        )
    );

-- Allow users to read participants from matches they played in
CREATE POLICY "Users can read participants from their matches"
    ON public.match_participants
    FOR SELECT
    USING (
        match_id IN (
            SELECT match_id FROM public.match_participants mp
            WHERE mp.puuid IN (
                SELECT puuid FROM public.user_summoners
                WHERE user_id = auth.uid()
            )
        )
    );

-- ============================================
-- Migration Complete!
-- ============================================
