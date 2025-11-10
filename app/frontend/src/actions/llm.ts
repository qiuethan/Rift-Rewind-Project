/**
 * LLM Actions - AI-powered analysis endpoints
 */
import { apiClient } from '@/api/client';

export interface AnalysisResponse {
  summary: string;
  full_analysis: string;
  model_used: string;
  contexts_used: string[];
}

export interface ChampionAnalysisResponse extends AnalysisResponse {
  champion_id: number;
}

export interface MatchAnalysisResponse extends AnalysisResponse {
  match_id: string;
}

/**
 * Generate AI analysis for a champion
 */
export const analyzeChampion = async (championId: number): Promise<{
  success: boolean;
  data?: ChampionAnalysisResponse;
  error?: string;
}> => {
  try {
    const data = await apiClient.post<ChampionAnalysisResponse>(`/api/llm/analyze-champion?champion_id=${championId}`);
    return {
      success: true,
      data,
    };
  } catch (error: any) {
    console.error('Error generating champion analysis:', error);
    return {
      success: false,
      error: error.message || 'Failed to generate champion analysis',
    };
  }
};

/**
 * Generate AI analysis for a match
 */
export const analyzeMatch = async (matchId: string): Promise<{
  success: boolean;
  data?: MatchAnalysisResponse;
  error?: string;
}> => {
  try {
    const data = await apiClient.post<MatchAnalysisResponse>(`/api/llm/analyze-match?match_id=${matchId}`);
    return {
      success: true,
      data,
    };
  } catch (error: any) {
    console.error('Error generating match analysis:', error);
    return {
      success: false,
      error: error.message || 'Failed to generate match analysis',
    };
  }
};

export const llmActions = {
  analyzeChampion,
  analyzeMatch,
};
