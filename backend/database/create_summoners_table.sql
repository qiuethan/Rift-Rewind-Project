-- Create summoners table first (stores actual League account data)
CREATE TABLE IF NOT EXISTS public.summoners (
    puuid TEXT PRIMARY KEY,
    summoner_name TEXT NOT NULL,
    game_name TEXT,
    tag_line TEXT,
    region TEXT NOT NULL,
    summoner_level INTEGER NOT NULL DEFAULT 0,
    profile_icon_id INTEGER NOT NULL DEFAULT 0,
    last_updated TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Create user_summoners junction table (many-to-many relationship)
-- This allows multiple users to link the same League account
CREATE TABLE IF NOT EXISTS public.user_summoners (
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
CREATE INDEX IF NOT EXISTS idx_user_summoners_user_id ON public.user_summoners(user_id);
CREATE INDEX IF NOT EXISTS idx_user_summoners_puuid ON public.user_summoners(puuid);

-- Create indexes for summoners
CREATE INDEX IF NOT EXISTS idx_summoners_game_name ON public.summoners(game_name);
CREATE INDEX IF NOT EXISTS idx_summoners_region ON public.summoners(region);

-- Enable Row Level Security on user_summoners
ALTER TABLE public.user_summoners ENABLE ROW LEVEL SECURITY;

-- Policy: Users can view their own linked accounts
CREATE POLICY "Users can view own links"
    ON public.user_summoners
    FOR SELECT
    USING (auth.uid() = user_id);

-- Policy: Users can insert their own links
CREATE POLICY "Users can insert own links"
    ON public.user_summoners
    FOR INSERT
    WITH CHECK (auth.uid() = user_id);

-- Policy: Users can delete their own links
CREATE POLICY "Users can delete own links"
    ON public.user_summoners
    FOR DELETE
    USING (auth.uid() = user_id);

-- Enable Row Level Security on summoners
ALTER TABLE public.summoners ENABLE ROW LEVEL SECURITY;

-- Policy: Anyone can read summoner data (public profiles)
CREATE POLICY "Anyone can view summoners"
    ON public.summoners
    FOR SELECT
    USING (true);

-- Policy: System can insert/update summoner data (via service role)
-- Users cannot directly modify summoner data, only link/unlink via user_summoners

-- Create function to update updated_at timestamp
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

-- Note: user_summoners doesn't need updated_at since links don't change
