/**
 * Analysis Cache Utility
 * Stores AI-generated analyses in localStorage
 */

const CACHE_KEY_PREFIX = 'rift_analysis_';

export interface CachedAnalysis {
  summary: string;
  fullAnalysis: string;
  timestamp: number;
  lastGameTimestamp?: number; // For champion analyses - timestamp of most recent game
}

/**
 * Get cached analysis for a match
 */
export const getCachedMatchAnalysis = (matchId: string): CachedAnalysis | null => {
  try {
    const key = `${CACHE_KEY_PREFIX}match_${matchId}`;
    const cached = localStorage.getItem(key);
    if (cached) {
      return JSON.parse(cached);
    }
  } catch (error) {
    console.error('Error reading match analysis from cache:', error);
  }
  return null;
};

/**
 * Cache analysis for a match
 */
export const cacheMatchAnalysis = (matchId: string, analysis: { summary: string; fullAnalysis: string }): void => {
  try {
    const key = `${CACHE_KEY_PREFIX}match_${matchId}`;
    const cached: CachedAnalysis = {
      ...analysis,
      timestamp: Date.now(),
    };
    localStorage.setItem(key, JSON.stringify(cached));
  } catch (error) {
    console.error('Error caching match analysis:', error);
  }
};

/**
 * Get cached analysis for a champion
 */
export const getCachedChampionAnalysis = (championId: number): CachedAnalysis | null => {
  try {
    const key = `${CACHE_KEY_PREFIX}champion_${championId}`;
    const cached = localStorage.getItem(key);
    if (cached) {
      return JSON.parse(cached);
    }
  } catch (error) {
    console.error('Error reading champion analysis from cache:', error);
  }
  return null;
};

/**
 * Cache analysis for a champion
 */
export const cacheChampionAnalysis = (
  championId: number, 
  analysis: { summary: string; fullAnalysis: string },
  lastGameTimestamp?: number
): void => {
  try {
    const key = `${CACHE_KEY_PREFIX}champion_${championId}`;
    const cached: CachedAnalysis = {
      ...analysis,
      timestamp: Date.now(),
      lastGameTimestamp,
    };
    localStorage.setItem(key, JSON.stringify(cached));
  } catch (error) {
    console.error('Error caching champion analysis:', error);
  }
};

/**
 * Check if cached champion analysis is still valid
 * Returns true if cache exists and no new games have been played since caching
 */
export const isChampionCacheValid = (championId: number, currentLastGameTimestamp: number): boolean => {
  try {
    const cached = getCachedChampionAnalysis(championId);
    if (!cached) {
      return false;
    }
    
    // If we don't have a lastGameTimestamp in cache, consider it invalid (old cache format)
    if (!cached.lastGameTimestamp) {
      return false;
    }
    
    // Cache is valid if the last game timestamp hasn't changed
    return cached.lastGameTimestamp === currentLastGameTimestamp;
  } catch (error) {
    console.error('Error checking champion cache validity:', error);
    return false;
  }
};

/**
 * Clear all cached analyses
 * Called on logout or account linking
 */
export const clearAllAnalysisCache = (): void => {
  try {
    const keys = Object.keys(localStorage);
    keys.forEach(key => {
      if (key.startsWith(CACHE_KEY_PREFIX)) {
        localStorage.removeItem(key);
      }
    });
    console.log('Cleared all analysis cache');
  } catch (error) {
    console.error('Error clearing analysis cache:', error);
  }
};
