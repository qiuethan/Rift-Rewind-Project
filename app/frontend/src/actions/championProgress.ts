/**
 * Champion Progress Actions
 * Business logic for champion progress operations
 */
import * as championProgressApi from '@/api/championProgress';
import type {
  ChampionProgressResponse,
  AllChampionsProgressResponse,
} from '@/api/championProgress';

interface ActionResult<T> {
  success: boolean;
  data?: T;
  error?: string;
}

export const championProgressActions = {
  /**
   * Get progress data for a specific champion
   */
  getChampionProgress: async (
    championId: number,
    limit: number = 10
  ): Promise<ActionResult<ChampionProgressResponse>> => {
    try {
      const data = await championProgressApi.getChampionProgress(championId, limit);
      return { success: true, data };
    } catch (error) {
      console.error('Failed to fetch champion progress:', error);
      return {
        success: false,
        error: error instanceof Error ? error.message : 'Failed to fetch champion progress',
      };
    }
  },

  /**
   * Get progress data for all champions
   */
  getAllChampionsProgress: async (): Promise<ActionResult<AllChampionsProgressResponse>> => {
    try {
      const data = await championProgressApi.getAllChampionsProgress();
      return { success: true, data };
    } catch (error) {
      console.error('Failed to fetch all champions progress:', error);
      return {
        success: false,
        error: error instanceof Error ? error.message : 'Failed to fetch champions progress',
      };
    }
  },
};
