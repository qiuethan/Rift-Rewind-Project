import { playersApi, SummonerRequest } from '@/api/players';

export const playersActions = {
  /**
   * Link a League of Legends summoner account
   */
  linkSummoner: async (data: SummonerRequest) => {
    try {
      const summoner = await playersApi.linkSummoner(data);
      return { success: true, data: summoner };
    } catch (error) {
      return {
        success: false,
        error: error instanceof Error ? error.message : 'Failed to link summoner',
      };
    }
  },

  /**
   * Link account using Riot ID (game_name + tag_line)
   */
  linkAccount: async (data: SummonerRequest) => {
    try {
      const summoner = await playersApi.linkSummoner(data);
      return { success: true, data: summoner };
    } catch (error) {
      return {
        success: false,
        error: error instanceof Error ? error.message : 'Failed to link account',
      };
    }
  },

  /**
   * Get linked summoner account
   */
  getSummoner: async () => {
    try {
      const summoner = await playersApi.getSummoner();
      return { success: true, data: summoner };
    } catch (error) {
      return {
        success: false,
        error: error instanceof Error ? error.message : 'Failed to get summoner',
      };
    }
  },

  /**
   * Get player statistics
   */
  getPlayerStats: async (summonerId: string) => {
    try {
      const stats = await playersApi.getPlayerStats(summonerId);
      return { success: true, data: stats };
    } catch (error) {
      return {
        success: false,
        error: error instanceof Error ? error.message : 'Failed to get player stats',
      };
    }
  },

  /**
   * Get match history
   */
  getMatchHistory: async (count: number = 20) => {
    try {
      const matches = await playersApi.getMatchHistory(count);
      return { success: true, data: matches };
    } catch (error) {
      return {
        success: false,
        error: error instanceof Error ? error.message : 'Failed to get match history',
      };
    }
  },
};
