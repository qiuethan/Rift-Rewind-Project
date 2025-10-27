-- Create summoners table in Supabase
CREATE TABLE IF NOT EXISTS public.summoners (
    id TEXT PRIMARY KEY,
    user_id UUID NOT NULL,
    summoner_name TEXT NOT NULL,
    game_name TEXT,
    tag_line TEXT,
    region TEXT NOT NULL,
    puuid TEXT NOT NULL,
    summoner_level INTEGER NOT NULL DEFAULT 0,
    profile_icon_id INTEGER NOT NULL DEFAULT 0,
    last_updated TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    
    -- Foreign key to auth.users
    CONSTRAINT fk_user FOREIGN KEY (user_id) REFERENCES auth.users(id) ON DELETE CASCADE
);

-- Create index on user_id for faster lookups
CREATE INDEX IF NOT EXISTS idx_summoners_user_id ON public.summoners(user_id);

-- Create index on puuid for Riot API lookups
CREATE INDEX IF NOT EXISTS idx_summoners_puuid ON public.summoners(puuid);

-- Enable Row Level Security
ALTER TABLE public.summoners ENABLE ROW LEVEL SECURITY;

-- Policy: Users can view own summoner
CREATE POLICY "Users can view own summoner"
    ON public.summoners
    FOR SELECT
    USING (auth.uid() = user_id);

-- Policy: Users can insert their own summoner data
CREATE POLICY "Users can insert own summoner"
    ON public.summoners
    FOR INSERT
    WITH CHECK (auth.uid() = user_id);

-- Policy: Users can update their own summoner data
CREATE POLICY "Users can update own summoner"
    ON public.summoners
    FOR UPDATE
    USING (auth.uid() = user_id);

-- Policy: Users can delete their own summoner data
CREATE POLICY "Users can delete own summoner"
    ON public.summoners
    FOR DELETE
    USING (auth.uid() = user_id);

-- Create function to update updated_at timestamp
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Create trigger to automatically update updated_at
CREATE TRIGGER update_summoners_updated_at
    BEFORE UPDATE ON public.summoners
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();
