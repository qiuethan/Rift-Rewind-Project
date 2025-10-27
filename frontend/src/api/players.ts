import { apiClient } from './client';

export interface SummonerRequest {
  summoner_name: string;
  region: string;
  tag_line?: string;
}

export interface SummonerResponse {
  id: string;
  summoner_name: string;
  region: string;
  puuid: string;
  summoner_level: number;
  profile_icon_id: number;
  last_updated: string;
}

export interface PlayerStatsResponse {
  summoner_id: string;
  total_games: number;
  wins: number;
  losses: number;
  win_rate: number;
  favorite_champions: string[];
  average_kda: number;
  average_cs_per_min: number;
}

export const playersApi = {
  linkSummoner: async (data: SummonerRequest): Promise<SummonerResponse> => {
    return apiClient.post<SummonerResponse>('/api/players/summoner', data);
  },

  getSummoner: async (): Promise<SummonerResponse> => {
    return apiClient.get<SummonerResponse>('/api/players/summoner');
  },

  getPlayerStats: async (summonerId: string): Promise<PlayerStatsResponse> => {
    return apiClient.get<PlayerStatsResponse>(`/api/players/stats/${summonerId}`);
  },

  getMatchHistory: async (count: number = 20): Promise<string[]> => {
    return apiClient.get<string[]>(`/api/players/matches?count=${count}`);
  },
};
