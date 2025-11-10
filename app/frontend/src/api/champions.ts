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
  champion_title?: string;
  champion_tags?: string[];
  champion_image_url?: string;
  lore_snippet?: string;
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

export interface AbilitySimilarity {
  ability_type: string;
  ability_name: string;
  similar_champion: string;
  similar_ability_type: string;
  similar_ability_name: string;
  similarity_score: number;
  explanation: string;
}

export interface AbilitySimilarityResponse {
  champion_id: string;
  champion_name: string;
  abilities: AbilitySimilarity[];
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

  getAbilitySimilarities: async (
    championId: string,
    limitPerAbility: number = 3
  ): Promise<AbilitySimilarityResponse> => {
    return apiClient.get<AbilitySimilarityResponse>(
      `/api/champions/${championId}/ability-similarities?limit_per_ability=${limitPerAbility}`
    );
  },
};
