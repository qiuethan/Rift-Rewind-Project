-- Migration: Add summoners tracking to matches table
-- Purpose: Track which summoners have been processed for each match
-- This allows multiple players who played in the same match to link accounts
-- without re-fetching the match data from Riot API

-- Add summoners column (array of PUUIDs)
ALTER TABLE matches 
ADD COLUMN IF NOT EXISTS summoners TEXT[] DEFAULT '{}';

-- Create index for faster lookups
CREATE INDEX IF NOT EXISTS idx_matches_summoners ON matches USING GIN (summoners);

-- Add comment for documentation
COMMENT ON COLUMN matches.summoners IS 'Array of summoner PUUIDs that have been processed for this match';
