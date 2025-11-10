/**
 * Tracked Champions API
 * Endpoints for managing user's tracked champions
 */
import { apiClient } from './client';

export interface TrackedChampion {
  champion_id: number;
  tracked_at: string;
}

export interface TrackedChampionsResponse {
  tracked_champions: TrackedChampion[];
  count: number;
  max_allowed: number;
}

export interface TrackChampionRequest {
  champion_id: number;
}

export interface TrackChampionResponse {
  message: string;
  champion_id: number;
  tracked_at: string;
}

/**
 * Get user's tracked champions
 */
export const getTrackedChampions = async (): Promise<TrackedChampionsResponse> => {
  return apiClient.get<TrackedChampionsResponse>('/api/tracked-champions');
};

/**
 * Track a champion
 */
export const trackChampion = async (championId: number): Promise<TrackChampionResponse> => {
  return apiClient.post<TrackChampionResponse>('/api/tracked-champions', {
    champion_id: championId,
  });
};

/**
 * Untrack a champion
 */
export const untrackChampion = async (championId: number): Promise<{ message: string }> => {
  return apiClient.delete<{ message: string }>(`/api/tracked-champions/${championId}`);
};

export default {
  getTrackedChampions,
  trackChampion,
  untrackChampion,
};
