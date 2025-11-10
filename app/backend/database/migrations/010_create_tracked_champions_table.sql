-- Migration: Create tracked_champions table
-- Description: Allows users to track up to 3 champions for quick access

CREATE TABLE IF NOT EXISTS tracked_champions (
    id SERIAL PRIMARY KEY,
    user_id UUID NOT NULL REFERENCES auth.users(id) ON DELETE CASCADE,
    champion_id INTEGER NOT NULL,
    tracked_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    UNIQUE(user_id, champion_id)
);

-- Create index for faster lookups
CREATE INDEX IF NOT EXISTS idx_tracked_champions_user_id ON tracked_champions(user_id);

-- Add constraint to limit 3 champions per user
-- This will be enforced in the application logic as well
CREATE OR REPLACE FUNCTION check_tracked_champions_limit()
RETURNS TRIGGER AS $$
BEGIN
    IF (SELECT COUNT(*) FROM tracked_champions WHERE user_id = NEW.user_id) >= 3 THEN
        RAISE EXCEPTION 'User can only track up to 3 champions';
    END IF;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER enforce_tracked_champions_limit
    BEFORE INSERT ON tracked_champions
    FOR EACH ROW
    EXECUTE FUNCTION check_tracked_champions_limit();
