-- ============================================
-- Rift Rewind Database Setup - Complete Schema
-- Run this file to create all tables from scratch
-- ============================================

-- Drop existing tables if they exist (in reverse order of dependencies)
DROP TABLE IF EXISTS public.champion_masteries CASCADE;
DROP TABLE IF EXISTS public.user_summoners CASCADE;
DROP TABLE IF EXISTS public.summoners CASCADE;

-- ============================================
-- 1. Create summoners table (stores League account data)
-- ============================================
CREATE TABLE public.summoners (
    puuid TEXT PRIMARY KEY,
    summoner_name TEXT NOT NULL,
    game_name TEXT,
    tag_line TEXT,
    region TEXT NOT NULL,
    summoner_level INTEGER NOT NULL DEFAULT 0,
    profile_icon_id INTEGER NOT NULL DEFAULT 0,
    
    -- Ranked information
    ranked_solo_tier TEXT,
    ranked_solo_rank TEXT,
    ranked_solo_lp INTEGER,
    ranked_solo_wins INTEGER,
    ranked_solo_losses INTEGER,
    ranked_flex_tier TEXT,
    ranked_flex_rank TEXT,
    
    -- Champion mastery data (stored as JSONB for flexibility)
    champion_masteries JSONB,
    total_mastery_score INTEGER DEFAULT 0,
    
    last_updated TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Create indexes for summoners
CREATE INDEX idx_summoners_game_name ON public.summoners(game_name);
CREATE INDEX idx_summoners_region ON public.summoners(region);
CREATE INDEX idx_summoners_mastery_score ON public.summoners(total_mastery_score DESC);

-- Enable Row Level Security on summoners (policies created later)
ALTER TABLE public.summoners ENABLE ROW LEVEL SECURITY;

-- ============================================
-- 2. Create user_summoners junction table (many-to-many relationship)
-- ============================================
CREATE TABLE public.user_summoners (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL,
    puuid TEXT NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    
    -- Foreign key to auth.users
    CONSTRAINT fk_user FOREIGN KEY (user_id) REFERENCES auth.users(id) ON DELETE CASCADE,
    
    -- Foreign key to summoners (REQUIRED for Supabase JOIN)
    CONSTRAINT fk_summoner FOREIGN KEY (puuid) REFERENCES public.summoners(puuid) ON DELETE CASCADE,
    
    -- Unique constraint: one user can only link a specific account once
    CONSTRAINT unique_user_summoner UNIQUE (user_id, puuid)
);

-- Create indexes for user_summoners
CREATE INDEX idx_user_summoners_user_id ON public.user_summoners(user_id);
CREATE INDEX idx_user_summoners_puuid ON public.user_summoners(puuid);

-- Enable Row Level Security on user_summoners (policies created later)
ALTER TABLE public.user_summoners ENABLE ROW LEVEL SECURITY;

-- ============================================
-- 3. Create champion_masteries table (detailed mastery data)
-- ============================================
CREATE TABLE public.champion_masteries (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    puuid TEXT NOT NULL,
    champion_id INTEGER NOT NULL,
    champion_level INTEGER NOT NULL,
    champion_points INTEGER NOT NULL,
    last_play_time BIGINT,
    champion_points_since_last_level INTEGER NOT NULL DEFAULT 0,
    champion_points_until_next_level INTEGER NOT NULL DEFAULT 0,
    chest_granted BOOLEAN NOT NULL DEFAULT FALSE,
    tokens_earned INTEGER NOT NULL DEFAULT 0,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    
    -- Foreign key to summoners
    CONSTRAINT fk_summoner FOREIGN KEY (puuid) REFERENCES public.summoners(puuid) ON DELETE CASCADE,
    
    -- Unique constraint: one mastery record per champion per summoner
    CONSTRAINT unique_summoner_champion UNIQUE (puuid, champion_id)
);

-- Create indexes for champion_masteries
CREATE INDEX idx_champion_masteries_puuid ON public.champion_masteries(puuid);
CREATE INDEX idx_champion_masteries_champion_id ON public.champion_masteries(champion_id);
CREATE INDEX idx_champion_masteries_champion_points ON public.champion_masteries(champion_points DESC);
CREATE INDEX idx_champion_masteries_champion_level ON public.champion_masteries(champion_level DESC);

-- Enable Row Level Security (policies created later)
ALTER TABLE public.champion_masteries ENABLE ROW LEVEL SECURITY;

-- ============================================
-- 4. Create triggers and functions
-- ============================================

-- Function to automatically update updated_at column
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Create trigger to automatically update updated_at on summoners
CREATE TRIGGER update_summoners_updated_at
    BEFORE UPDATE ON public.summoners
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

-- Create trigger to automatically update updated_at on champion_masteries
CREATE TRIGGER update_champion_masteries_updated_at
    BEFORE UPDATE ON public.champion_masteries
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

-- ============================================
-- 5. Create Row Level Security Policies (after all tables exist)
-- ============================================

-- Policies for summoners table
CREATE POLICY "Users can read their linked summoners"
    ON public.summoners
    FOR SELECT
    USING (
        puuid IN (
            SELECT puuid FROM public.user_summoners
            WHERE user_id = auth.uid()
        )
    );

CREATE POLICY "Service role can manage all summoners"
    ON public.summoners
    FOR ALL
    USING (auth.role() = 'service_role');

-- Policies for user_summoners table
CREATE POLICY "Users can read their own summoner links"
    ON public.user_summoners
    FOR SELECT
    USING (user_id = auth.uid());

CREATE POLICY "Service role can manage all summoner links"
    ON public.user_summoners
    FOR ALL
    USING (auth.role() = 'service_role');

-- Policies for champion_masteries table
CREATE POLICY "Users can read their own champion masteries"
    ON public.champion_masteries
    FOR SELECT
    USING (
        puuid IN (
            SELECT puuid FROM public.user_summoners
            WHERE user_id = auth.uid()
        )
    );

CREATE POLICY "Service role can manage all champion masteries"
    ON public.champion_masteries
    FOR ALL
    USING (auth.role() = 'service_role');

-- ============================================
-- Setup Complete!
-- ============================================
