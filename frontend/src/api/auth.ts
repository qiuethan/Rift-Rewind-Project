import { apiClient } from './client';

export interface RegisterRequest {
  email: string;
  password: string;
  summoner_name?: string;
  region?: string;
}

export interface LoginRequest {
  email: string;
  password: string;
}

export interface AuthResponse {
  user_id: string;
  email: string;
  token: string;
  summoner_name?: string;
  region?: string;
}

export interface TokenResponse {
  user_id: string;
  email: string;
  valid: boolean;
}

export const authApi = {
  register: async (data: RegisterRequest): Promise<AuthResponse> => {
    return apiClient.post<AuthResponse>('/api/auth/register', data);
  },

  login: async (data: LoginRequest): Promise<AuthResponse> => {
    return apiClient.post<AuthResponse>('/api/auth/login', data);
  },

  verifyToken: async (): Promise<TokenResponse> => {
    return apiClient.get<TokenResponse>('/api/auth/verify');
  },

  getCurrentUser: async (): Promise<AuthResponse> => {
    return apiClient.get<AuthResponse>('/api/auth/me');
  },
};
