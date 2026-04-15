'use client';

import React, { createContext, useContext, useEffect } from 'react';
import { useAuthStore } from '@/store/useAuthStore';
import api from '@/lib/api-client';

const AuthContext = createContext<{}>({});

export function AuthProvider({ children }: { children: React.ReactNode }) {
  const { setAuth, logout, setLoading } = useAuthStore();

  useEffect(() => {
    async function initAuth() {
      const token = localStorage.getItem('auth_token');
      if (!token) return;

      setLoading(true);
      try {
        // Verify token by getting current user
        const response = await api.get('/auth/me');
        setAuth(response.data, token);
      } catch (error) {
        console.error('Failed to restore session:', error);
        logout();
      } finally {
        setLoading(false);
      }
    }

    initAuth();
  }, [setAuth, logout, setLoading]);

  return (
    <AuthContext.Provider value={{}}>
      {children}
    </AuthContext.Provider>
  );
}

export const useAuth = () => useContext(AuthContext);
