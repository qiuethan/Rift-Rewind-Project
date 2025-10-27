import { apiClient } from './client';

export interface PerformanceAnalysisRequest {
  match_id: string;
  summoner_id: string;
  include_timeline?: boolean;
}

export interface PerformanceMetrics {
  match_id: string;
  participant_id: number;
  kda: number;
  cs_per_min: number;
  gold_per_min: number;
  damage_per_min: number;
  vision_score: number;
  kill_participation: number;
}

export interface GamePhaseAnalysis {
  phase: 'early' | 'mid' | 'late';
  cs_advantage: number;
  gold_advantage: number;
  xp_advantage: number;
  deaths: number;
  kills: number;
  assists: number;
}

export interface PerformanceAnalysisResponse {
  match_id: string;
  summoner_id: string;
  overall_grade: 'S' | 'A' | 'B' | 'C' | 'D' | 'F';
  metrics: PerformanceMetrics;
  phase_analysis: GamePhaseAnalysis[];
  strengths: string[];
  weaknesses: string[];
  recommendations: string[];
}

export interface InsightRequest {
  summoner_id: string;
  match_ids: string[];
  focus_areas?: string[];
}

export interface InsightResponse {
  summoner_id: string;
  insights: string[];
  key_patterns: string[];
  actionable_tips: string[];
  champion_pool_suggestions: string[];
}

export const analyticsApi = {
  analyzePerformance: async (
    data: PerformanceAnalysisRequest
  ): Promise<PerformanceAnalysisResponse> => {
    return apiClient.post<PerformanceAnalysisResponse>('/api/analytics/performance', data);
  },

  generateInsights: async (data: InsightRequest): Promise<InsightResponse> => {
    return apiClient.post<InsightResponse>('/api/analytics/insights', data);
  },
};
