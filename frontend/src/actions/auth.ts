import { RegisterRequest, LoginRequest, AuthResponse } from '@/api/auth';
import { supabase } from '@/lib/supabase';
import { STORAGE_KEYS } from '@/config';

export const authActions = {
  /**
   * Register a new user with Supabase
   */
  register: async (data: RegisterRequest) => {
    try {
      // Register with Supabase Auth
      const { data: authData, error: authError } = await supabase.auth.signUp({
        email: data.email,
        password: data.password,
      });

      if (authError) throw authError;
      
      // Check if email confirmation is required
      if (!authData.session && authData.user) {
        // Email confirmation required - return success with pending status
        return { 
          success: true, 
          data: { 
            user_id: authData.user.id,
            email: authData.user.email!,
            token: '',
            pending_confirmation: true,
          } 
        };
      }

      if (!authData.session) throw new Error('No session created');

      // Store token
      localStorage.setItem(STORAGE_KEYS.AUTH_TOKEN, authData.session.access_token);

      // Store user data
      const userData: AuthResponse = {
        user_id: authData.user!.id,
        email: authData.user!.email!,
        token: authData.session.access_token,
        summoner_name: data.summoner_name,
        region: data.region,
      };
      localStorage.setItem(STORAGE_KEYS.USER_DATA, JSON.stringify(userData));

      return { success: true, data: userData };
    } catch (error) {
      return {
        success: false,
        error: error instanceof Error ? error.message : 'Registration failed',
      };
    }
  },

  /**
   * Login user with Supabase
   */
  login: async (data: LoginRequest) => {
    try {
      // Login with Supabase Auth
      const { data: authData, error: authError } = await supabase.auth.signInWithPassword({
        email: data.email,
        password: data.password,
      });

      if (authError) throw authError;
      if (!authData.session) throw new Error('No session created');

      // Store token
      localStorage.setItem(STORAGE_KEYS.AUTH_TOKEN, authData.session.access_token);

      // Store user data
      const userData: AuthResponse = {
        user_id: authData.user!.id,
        email: authData.user!.email!,
        token: authData.session.access_token,
      };
      localStorage.setItem(STORAGE_KEYS.USER_DATA, JSON.stringify(userData));

      return { success: true, data: userData };
    } catch (error) {
      return {
        success: false,
        error: error instanceof Error ? error.message : 'Login failed',
      };
    }
  },

  /**
   * Logout user
   */
  logout: async () => {
    try {
      await supabase.auth.signOut();
      localStorage.removeItem(STORAGE_KEYS.AUTH_TOKEN);
      localStorage.removeItem(STORAGE_KEYS.USER_DATA);
      return { success: true, data: null };
    } catch (error) {
      return {
        success: false,
        error: error instanceof Error ? error.message : 'Logout failed',
      };
    }
  },

  /**
   * Check if user is authenticated
   */
  isAuthenticated: (): boolean => {
    const token = localStorage.getItem(STORAGE_KEYS.AUTH_TOKEN);
    return !!token;
  },

  /**
   * Get current user data from localStorage
   */
  getCurrentUser: (): AuthResponse | null => {
    const userData = localStorage.getItem(STORAGE_KEYS.USER_DATA);
    if (!userData) return null;
    try {
      return JSON.parse(userData);
    } catch {
      return null;
    }
  },

  /**
   * Verify token is still valid
   */
  verifyToken: async () => {
    try {
      const { data, error } = await supabase.auth.getSession();
      if (error) throw error;
      if (!data.session) throw new Error('No active session');

      return { success: true, data: { valid: true } };
    } catch (error) {
      localStorage.removeItem(STORAGE_KEYS.AUTH_TOKEN);
      localStorage.removeItem(STORAGE_KEYS.USER_DATA);
      return {
        success: false,
        error: error instanceof Error ? error.message : 'Token verification failed',
      };
    }
  },
};
