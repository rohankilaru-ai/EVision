/**
 * Authentication hook
 */
import { create } from 'zustand';
import { persist } from 'zustand/middleware';
import { apiClient } from '@/services/api';
import { User, TokenResponse } from '@/types';

interface AuthState {
  user: User | null;
  isAuthenticated: boolean;
  isLoading: boolean;
  error: string | null;
  login: (tokenResponse: TokenResponse) => void;
  logout: () => void;
  fetchUser: () => Promise<void>;
  setError: (error: string | null) => void;
}

export const useAuthStore = create<AuthState>()(
  persist(
    (set, get) => ({
      user: null,
      isAuthenticated: false,
      isLoading: false,
      error: null,

      login: (tokenResponse: TokenResponse) => {
        apiClient.setToken(tokenResponse.access_token, tokenResponse.refresh_token);
        set({
          user: tokenResponse.user,
          isAuthenticated: true,
          error: null,
        });
      },

      logout: () => {
        apiClient.setToken('', '');
        set({
          user: null,
          isAuthenticated: false,
          error: null,
        });
      },

      fetchUser: async () => {
        set({ isLoading: true, error: null });
        try {
          const user = await apiClient.getCurrentUser();
          set({
            user,
            isAuthenticated: true,
            isLoading: false,
          });
        } catch (error: any) {
          set({
            user: null,
            isAuthenticated: false,
            isLoading: false,
            error: error.message || 'Failed to fetch user',
          });
        }
      },

      setError: (error: string | null) => {
        set({ error });
      },
    }),
    {
      name: 'auth-storage',
      partialize: (state) => ({
        user: state.user,
        isAuthenticated: state.isAuthenticated,
      }),
    }
  )
);

export const useAuth = () => {
  const { user, isAuthenticated, isLoading, error, login, logout, fetchUser, setError } =
    useAuthStore();

  return {
    user,
    isAuthenticated,
    isLoading,
    error,
    login,
    logout,
    fetchUser,
    setError,
  };
};
