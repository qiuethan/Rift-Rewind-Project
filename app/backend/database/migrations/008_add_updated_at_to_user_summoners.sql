-- Migration: Add updated_at column to user_summoners table
-- Purpose: Track when a user last updated their linked summoner account for rate limiting

-- Add updated_at column
ALTER TABLE public.user_summoners 
ADD COLUMN IF NOT EXISTS updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW();

-- Create trigger to automatically update updated_at
CREATE TRIGGER update_user_summoners_updated_at
    BEFORE UPDATE ON public.user_summoners
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

-- Add comment for documentation
COMMENT ON COLUMN public.user_summoners.updated_at IS 'Timestamp of last update, used for rate limiting account linking';
