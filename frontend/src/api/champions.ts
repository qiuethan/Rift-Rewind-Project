import { apiClient } from './client';

export interface ChampionData {
  id: string;
  name: string;
  title: string;
  tags: string[];
  stats: Record<string, number>;
  abilities: unknown[];
}

export interface ChampionRecommendationRequest {
  summoner_id: string;
  limit?: number;
  include_reasoning?: boolean;
}

export interface ChampionRecommendation {
  champion_id: string;
  champion_name: string;
  similarity_score: number;
  reasoning?: string;
  similar_abilities?: string[];
  playstyle_match?: string;
}

export interface ChampionRecommendationResponse {
  summoner_id: string;
  recommendations: ChampionRecommendation[];
  based_on_champions: string[];
}

export const championsApi = {
  getAllChampions: async (): Promise<ChampionData[]> => {
    return apiClient.get<ChampionData[]>('/api/champions/');
  },

  getChampion: async (championId: string): Promise<ChampionData> => {
    return apiClient.get<ChampionData>(`/api/champions/${championId}`);
  },

  getRecommendations: async (
    data: ChampionRecommendationRequest
  ): Promise<ChampionRecommendationResponse> => {
    return apiClient.post<ChampionRecommendationResponse>('/api/champions/recommendations', data);
  },
};
