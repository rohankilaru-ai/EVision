/**
 * API client for backend communication
 */
import axios, { AxiosInstance, AxiosRequestConfig } from 'axios';

const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000/api/v1';

class APIClient {
  private client: AxiosInstance;

  constructor() {
    this.client = axios.create({
      baseURL: API_URL,
      headers: {
        'Content-Type': 'application/json',
      },
    });

    // Add auth token to requests
    this.client.interceptors.request.use((config) => {
      const token = this.getToken();
      if (token) {
        config.headers.Authorization = `Bearer ${token}`;
      }
      return config;
    });

    // Handle auth errors
    this.client.interceptors.response.use(
      (response) => response,
      async (error) => {
        if (error.response?.status === 401) {
          // Token expired or invalid
          this.clearToken();
          window.location.href = '/login';
        }
        return Promise.reject(error);
      }
    );
  }

  private getToken(): string | null {
    if (typeof window === 'undefined') return null;
    return localStorage.getItem('access_token');
  }

  private clearToken(): void {
    if (typeof window === 'undefined') return;
    localStorage.removeItem('access_token');
    localStorage.removeItem('refresh_token');
  }

  setToken(accessToken: string, refreshToken?: string): void {
    if (typeof window === 'undefined') return;
    localStorage.setItem('access_token', accessToken);
    if (refreshToken) {
      localStorage.setItem('refresh_token', refreshToken);
    }
  }

  // Auth endpoints
  async googleAuth(code: string, redirectUri: string) {
    const response = await this.client.post('/auth/google', { code, redirect_uri: redirectUri });
    return response.data;
  }

  async getCurrentUser() {
    const response = await this.client.get('/auth/me');
    return response.data;
  }

  async refreshToken() {
    const refreshToken = localStorage.getItem('refresh_token');
    if (!refreshToken) throw new Error('No refresh token');

    const response = await this.client.post('/auth/refresh', null, {
      headers: { Authorization: `Bearer ${refreshToken}` },
    });
    return response.data;
  }

  // Markets endpoints
  async getKalshiMarkets(params?: {
    sport?: string;
    is_active?: boolean;
    limit?: number;
  }) {
    const response = await this.client.get('/markets/kalshi', { params });
    return response.data;
  }

  async getSportsbookOdds(params?: {
    sport?: string;
    sportsbook?: string;
    limit?: number;
  }) {
    const response = await this.client.get('/markets/sportsbook-odds', { params });
    return response.data;
  }

  async getEVOpportunities(params?: {
    sport?: string;
    min_edge?: number;
    min_ev?: number;
    is_active?: boolean;
    is_recommended?: boolean;
    page?: number;
    page_size?: number;
  }) {
    const response = await this.client.get('/markets/ev-opportunities', { params });
    return response.data;
  }

  async getEVOpportunity(id: number) {
    const response = await this.client.get(`/markets/ev-opportunities/${id}`);
    return response.data;
  }

  async runBacktest(data: {
    sport?: string;
    start_date: string;
    end_date: string;
    min_edge?: number;
    max_time_to_event_hours?: number;
  }) {
    const response = await this.client.post('/markets/backtest', data);
    return response.data;
  }

  async getStatsSummary(days: number = 7) {
    const response = await this.client.get('/markets/stats/summary', { params: { days } });
    return response.data;
  }
}

export const apiClient = new APIClient();
