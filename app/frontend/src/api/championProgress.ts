/**
 * Champion Progress API
 * Handles fetching champion-specific progress and statistics
 */
import { apiClient } from './client';

export interface ChampionMatchScore {
  match_id: string;
  champion_id: number;
  champion_name: string;
  game_date: number;
  eps_score: number;
  cps_score: number;
  kda: number;
  win: boolean;
  kills: number;
  deaths: number;
  assists: number;
  cs: number;
  gold: number;
  damage: number;
  vision_score: number;
}

export interface ChampionProgressTrend {
  champion_id: number;
  champion_name: string;
  total_games: number;
  wins: number;
  losses: number;
  win_rate: number;
  avg_eps_score: number;
  avg_cps_score: number;
  avg_kda: number;
  recent_trend: number;  // Combined trend percentage (deprecated)
  eps_trend: number;  // EPS trend percentage per game
  cps_trend: number;  // CPS trend percentage per game
  last_played: number;
  mastery_level?: number;
  mastery_points?: number;
}

export interface ChampionProgressResponse {
  user_id: string;
  champion_id: number;
  champion_name: string;
  trend: ChampionProgressTrend;
  recent_matches: ChampionMatchScore[];
  performance_summary: any;
}

export interface AllChampionsProgressResponse {
  user_id: string;
  champions: ChampionProgressTrend[];
  total_champions_played: number;
  most_played_champion?: ChampionProgressTrend;
  best_performing_champion?: ChampionProgressTrend;
}

/**
 * Get progress data for a specific champion
 */
export const getChampionProgress = async (
  championId: number,
  limit: number = 10
): Promise<ChampionProgressResponse> => {
  return apiClient.get<ChampionProgressResponse>(
    `/api/champion-progress/champion/${championId}?limit=${limit}`
  );
};

/**
 * Get progress data for all champions
 */
export const getAllChampionsProgress = async (): Promise<AllChampionsProgressResponse> => {
  return apiClient.get<AllChampionsProgressResponse>('/api/champion-progress/all');
};
