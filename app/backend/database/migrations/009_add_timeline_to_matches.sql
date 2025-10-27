-- Migration: Add timeline_data column to matches table
-- Purpose: Store match timeline data from Riot API for detailed analysis

-- Add timeline_data column
ALTER TABLE public.matches 
ADD COLUMN IF NOT EXISTS timeline_data JSONB;

-- Create GIN index for timeline_data JSONB (allows efficient querying)
CREATE INDEX IF NOT EXISTS idx_matches_timeline_data ON public.matches USING GIN (timeline_data);

-- Add comment for documentation
COMMENT ON COLUMN public.matches.timeline_data IS 'Complete timeline data from Riot API including frames and events';
