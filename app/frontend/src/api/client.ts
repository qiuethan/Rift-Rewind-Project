/**
 * API Client - Axios instance with auth interceptors
 * DO NOT MODIFY THIS FILE
 * Auth headers are automatically injected
 */
import axios, { AxiosInstance, AxiosResponse, InternalAxiosRequestConfig } from 'axios';
import { API_BASE_URL, STORAGE_KEYS } from '@/config';

class ApiClient {
  private client: AxiosInstance;

  constructor() {
    this.client = axios.create({
      baseURL: API_BASE_URL,
      timeout: 30000, // 60 second timeout for production
      headers: {
        'Content-Type': 'application/json',
      },
    });

    // Request interceptor - auto-inject auth token
    this.client.interceptors.request.use(
      (config: InternalAxiosRequestConfig) => {
        const token = localStorage.getItem(STORAGE_KEYS.AUTH_TOKEN);
        if (token && config.headers) {
          config.headers.Authorization = `Bearer ${token}`;
        }
        return config;
      },
      (error) => Promise.reject(error)
    );

    // Response interceptor - handle errors
    this.client.interceptors.response.use(
      (response: AxiosResponse) => response.data,
      (error) => {
        if (error.response?.status === 401) {
          // Unauthorized - clear auth and redirect to login
          localStorage.removeItem(STORAGE_KEYS.AUTH_TOKEN);
          localStorage.removeItem(STORAGE_KEYS.USER_DATA);
          window.location.href = '/login';
          return Promise.reject(new Error('Unauthorized'));
        }
        
        // Extract error message from response detail
        let errorMessage = 'An error occurred';
        
        if (error.response?.data) {
          // Try to get detail from response
          if (typeof error.response.data === 'string') {
            errorMessage = error.response.data;
          } else if (error.response.data.detail) {
            errorMessage = error.response.data.detail;
          } else if (error.response.data.message) {
            errorMessage = error.response.data.message;
          }
        } else if (error.message) {
          errorMessage = error.message;
        }
        
        return Promise.reject(new Error(errorMessage));
      }
    );
  }

  async get<T>(url: string): Promise<T> {
    return this.client.get<T, T>(url);
  }

  async post<T>(url: string, data?: unknown): Promise<T> {
    return this.client.post<T, T>(url, data);
  }

  async put<T>(url: string, data?: unknown): Promise<T> {
    return this.client.put<T, T>(url, data);
  }

  async delete<T>(url: string): Promise<T> {
    return this.client.delete<T, T>(url);
  }

  async patch<T>(url: string, data?: unknown): Promise<T> {
    return this.client.patch<T, T>(url, data);
  }
}

export const apiClient = new ApiClient();
