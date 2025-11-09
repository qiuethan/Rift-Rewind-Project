/**
 * LLM API Client
 * Handles AI chat and analysis requests
 */
import { apiClient } from './client';

export interface ChatRequest {
  prompt: string;
  match_id?: string;
  champion_id?: number;
  page_context?: string;
}

export interface ChatResponse {
  text: string;
  model_used: string;
  complexity: string;
  contexts_used: string[];
  metadata?: {
    page_context?: string;
    champion_id?: number;
    match_id?: string;
  };
}

export interface AnalyzeMatchResponse {
  text: string;
  model_used: string;
  complexity: string;
  match_id: string;
}

export interface LLMHealthResponse {
  status: string;
  bedrock_available: boolean;
}

/**
 * Send a chat message to the AI
 */
export async function chat(request: ChatRequest): Promise<ChatResponse> {
  return apiClient.post<ChatResponse>('/api/llm/chat', request);
}

/**
 * Analyze a specific match
 */
export async function analyzeMatch(matchId: string): Promise<AnalyzeMatchResponse> {
  return apiClient.post<AnalyzeMatchResponse>('/api/llm/analyze-match', { match_id: matchId });
}

/**
 * Check LLM service health
 */
export async function checkHealth(): Promise<LLMHealthResponse> {
  return apiClient.get<LLMHealthResponse>('/api/llm/health');
}
