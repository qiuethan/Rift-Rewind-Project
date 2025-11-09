/**
 * Application constants
 * DO NOT modify API_BASE_URL - it's set via environment variables
 */

export const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000';

export const SUPABASE_URL = import.meta.env.VITE_SUPABASE_URL || '';
export const SUPABASE_ANON_KEY = import.meta.env.VITE_SUPABASE_ANON_KEY || '';

export const STORAGE_KEYS = {
  AUTH_TOKEN: 'rift_rewind_auth_token',
  USER_DATA: 'rift_rewind_user_data',
} as const;

export const ROUTES = {
  HOME: '/',
  LOGIN: '/login',
  REGISTER: '/register',
  DASHBOARD: '/dashboard',
  GAMES: '/games',
  MATCH: '/match/:matchId',
  ANALYTICS: '/analytics',
  CHAMPIONS: '/champions',
  PROFILE: '/profile',
  TEST_CHAT: '/test-chat',
} as const;
