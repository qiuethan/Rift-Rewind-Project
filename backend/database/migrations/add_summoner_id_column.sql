-- Migration: Add summoner_id column to summoners table
-- This stores the encrypted summoner ID needed for ranked API lookups
-- Riot API v4 no longer returns this in the summoner-by-puuid endpoint

ALTER TABLE public.summoners 
ADD COLUMN IF NOT EXISTS summoner_id TEXT;

-- Create index for faster lookups
CREATE INDEX IF NOT EXISTS idx_summoners_summoner_id ON public.summoners(summoner_id);

-- Add comment
COMMENT ON COLUMN public.summoners.summoner_id IS 'Encrypted summoner ID for ranked API lookups (Riot API v4)';