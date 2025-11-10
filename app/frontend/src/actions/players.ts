import { playersApi, SummonerRequest } from '@/api/players';
import { clearAllAnalysisCache } from '@/utils/analysisCache';

export const playersActions = {
  /**
   * Link a League of Legends summoner account
   */
  linkSummoner: async (data: SummonerRequest) => {
    try {
      const summoner = await playersApi.linkSummoner(data);
      // Clear cached analyses when linking new summoner
      clearAllAnalysisCache();
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
      // Clear cached analyses when linking new account
      clearAllAnalysisCache();
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

  /**
   * Get recent games
   */
  getRecentGames: async (count: number = 5) => {
    try {
      const games = await playersApi.getRecentGames(count);
      return { success: true, data: games };
    } catch (error) {
      return {
        success: false,
        error: error instanceof Error ? error.message : 'Failed to get recent games',
      };
    }
  },

  /**
   * Get games with full match and timeline data (paginated)
   */
  getGames: async (startIndex: number = 0, count: number = 10) => {
    try {
      const games = await playersApi.getGames(startIndex, count);
      return { success: true, data: games };
    } catch (error) {
      return {
        success: false,
        error: error instanceof Error ? error.message : 'Failed to get games',
      };
    }
  },

  /**
   * Get a specific match by match_id with full match data and timeline
   */
  getMatch: async (matchId: string) => {
    try {
      const match = await playersApi.getMatch(matchId);
      return { success: true, data: match };
    } catch (error) {
      return {
        success: false,
        error: error instanceof Error ? error.message : 'Failed to get match',
      };
    }
  },
};
