-- Migration: Add recent_games column and remove ranked columns
-- Date: 2025-10-27

-- Add recent_games column to summoners table
ALTER TABLE public.summoners
ADD COLUMN IF NOT EXISTS recent_games JSONB DEFAULT '[]'::jsonb;

-- Remove ranked columns from summoners table
ALTER TABLE public.summoners
DROP COLUMN IF EXISTS ranked_solo_tier,
DROP COLUMN IF EXISTS ranked_solo_rank,
DROP COLUMN IF EXISTS ranked_solo_lp,
DROP COLUMN IF EXISTS ranked_solo_wins,
DROP COLUMN IF EXISTS ranked_solo_losses,
DROP COLUMN IF EXISTS ranked_flex_tier,
DROP COLUMN IF EXISTS ranked_flex_rank,
DROP COLUMN IF EXISTS ranked_flex_lp,
DROP COLUMN IF EXISTS ranked_flex_wins,
DROP COLUMN IF EXISTS ranked_flex_losses;

-- Add comment to recent_games column
COMMENT ON COLUMN public.summoners.recent_games IS 'Recent match history (JSONB array of game summaries)';
