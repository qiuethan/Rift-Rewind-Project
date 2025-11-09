-- Migration: Update trend columns from text to float
-- Description: Change recent_trend, eps_trend, and cps_trend from categorical strings to percentage values
-- Date: 2025-11-08

-- Step 1: Add new float columns
ALTER TABLE champion_progress 
ADD COLUMN recent_trend_new FLOAT DEFAULT 0.0,
ADD COLUMN eps_trend_new FLOAT DEFAULT 0.0,
ADD COLUMN cps_trend_new FLOAT DEFAULT 0.0;

-- Step 2: Migrate existing data (convert string categories to approximate percentages)
-- 'improving' -> 2.0%, 'declining' -> -2.0%, 'stable' -> 0.0%
UPDATE champion_progress
SET 
    recent_trend_new = CASE 
        WHEN recent_trend = 'improving' THEN 2.0
        WHEN recent_trend = 'declining' THEN -2.0
        ELSE 0.0
    END,
    eps_trend_new = CASE 
        WHEN eps_trend = 'improving' THEN 2.0
        WHEN eps_trend = 'declining' THEN -2.0
        ELSE 0.0
    END,
    cps_trend_new = CASE 
        WHEN cps_trend = 'improving' THEN 2.0
        WHEN cps_trend = 'declining' THEN -2.0
        ELSE 0.0
    END;

-- Step 3: Drop old columns
ALTER TABLE champion_progress
DROP COLUMN recent_trend,
DROP COLUMN eps_trend,
DROP COLUMN cps_trend;

-- Step 4: Rename new columns to original names
ALTER TABLE champion_progress
RENAME COLUMN recent_trend_new TO recent_trend;

ALTER TABLE champion_progress
RENAME COLUMN eps_trend_new TO eps_trend;

ALTER TABLE champion_progress
RENAME COLUMN cps_trend_new TO cps_trend;

-- Step 5: Add comments
COMMENT ON COLUMN champion_progress.recent_trend IS 'Combined trend percentage per game (deprecated, use eps_trend/cps_trend)';
COMMENT ON COLUMN champion_progress.eps_trend IS 'EPS trend percentage per game (positive = improving, negative = declining)';
COMMENT ON COLUMN champion_progress.cps_trend IS 'CPS trend percentage per game (positive = improving, negative = declining)';
