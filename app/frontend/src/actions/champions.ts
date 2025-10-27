import { championsApi, ChampionRecommendationRequest } from '@/api/champions';

export const championsActions = {
  /**
   * Get all champions
   */
  getAllChampions: async () => {
    try {
      const champions = await championsApi.getAllChampions();
      return { success: true, data: champions };
    } catch (error) {
      return {
        success: false,
        error: error instanceof Error ? error.message : 'Failed to get champions',
      };
    }
  },

  /**
   * Get champion by ID
   */
  getChampion: async (championId: string) => {
    try {
      const champion = await championsApi.getChampion(championId);
      return { success: true, data: champion };
    } catch (error) {
      return {
        success: false,
        error: error instanceof Error ? error.message : 'Failed to get champion',
      };
    }
  },

  /**
   * Get champion recommendations
   */
  getRecommendations: async (data: ChampionRecommendationRequest) => {
    try {
      const recommendations = await championsApi.getRecommendations(data);
      return { success: true, data: recommendations };
    } catch (error) {
      return {
        success: false,
        error: error instanceof Error ? error.message : 'Failed to get recommendations',
      };
    }
  },
};
