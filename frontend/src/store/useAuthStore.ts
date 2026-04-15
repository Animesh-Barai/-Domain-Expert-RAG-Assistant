import { create } from 'zustand';
import { persist, createJSONStorage } from 'zustand/middleware';
import api from '@/lib/api-client';

interface User {
  id: string;
  email: string;
  full_name?: string;
}

interface AuthState {
  user: User | null;
  token: string | null;
  isAuthenticated: boolean;
  isLoading: boolean;
  error: string | null;

  // Actions
  login: (email: string, password: string) => Promise<void>;
  register: (email: string, password: string) => Promise<void>;
  setAuth: (user: User, token: string) => void;
  logout: () => void;
  setLoading: (isLoading: boolean) => void;
  setError: (error: string | null) => void;
}

export const useAuthStore = create<AuthState>()(
  persist(
    (set, get) => ({
      user: null,
      token: null,
      isAuthenticated: false,
      isLoading: false,
      error: null,

      setAuth: (user, token) => {
        set({ user, token, isAuthenticated: true, error: null });
      },

      login: async (email, password) => {
        set({ isLoading: true, error: null });
        try {
          const formData = new URLSearchParams();
          formData.append('username', email);
          formData.append('password', password);

          const response = await api.post('/auth/login', formData, {
            headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
          });

          const { access_token } = response.data;
          
          if (typeof window !== 'undefined') {
            localStorage.setItem('auth_token', access_token);
          }

          const userResponse = await api.get('/auth/me', {
            headers: { Authorization: `Bearer ${access_token}` },
          });

          get().setAuth(userResponse.data, access_token);
          set({ isLoading: false });
        } catch (error: any) {
          const message = error.response?.data?.detail || 'Authentication failed';
          set({ error: message, isLoading: false });
          throw error;
        }
      },

      register: async (email, password) => {
        set({ isLoading: true, error: null });
        try {
          await api.post('/auth/register', { email, password });
          await get().login(email, password);
        } catch (error: any) {
          const message = error.response?.data?.detail || 'Registration failed';
          set({ error: message, isLoading: false });
          throw error;
        }
      },

      logout: () => {
        if (typeof window !== 'undefined') {
          localStorage.removeItem('auth_token');
        }
        set({ user: null, token: null, isAuthenticated: false });
      },

      setLoading: (isLoading) => set({ isLoading }),
      setError: (error) => set({ error }),
    }),
    {
      name: 'auth-storage',
      storage: createJSONStorage(() => localStorage),
      partialize: (state) => ({ user: state.user, isAuthenticated: state.isAuthenticated }),
    }
  )
);
