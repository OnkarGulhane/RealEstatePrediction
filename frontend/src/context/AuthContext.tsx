'use client';

/**
 * GharScope Central Authentication Context
 * Manages in-memory session, CSRF bootstrap, and automatic reload rehydration.
 */

import React, { createContext, useContext, useEffect, useState, useCallback } from 'react';
import type { UserProfile, AuthSuccessResponse } from '../types';
import {
  apiFetch,
  setAccessToken,
  clearSession,
  bootstrapCsrf,
  refreshAccessToken,
} from '../lib/api-client';

interface AuthContextType {
  user: UserProfile | null;
  authReady: boolean;
  login: (email: string, password: string) => Promise<void>;
  logout: () => Promise<void>;
  refreshProfile: () => Promise<void>;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

export function AuthProvider({ children }: { children: React.ReactNode }) {
  const [user, setUser] = useState<UserProfile | null>(null);
  const [authReady, setAuthReady] = useState(false);

  const fetchProfile = useCallback(async () => {
    try {
      const profile = await apiFetch<UserProfile>('/auth/me/');
      setUser(profile);
    } catch {
      setUser(null);
    }
  }, []);

  useEffect(() => {
    let isMounted = true;

    async function initSession() {
      try {
        // Step 1: Bootstrap CSRF token & cookie
        await bootstrapCsrf();

        // Step 2: Attempt refresh via HttpOnly cookie
        const token = await refreshAccessToken();
        if (token && isMounted) {
          await fetchProfile();
        }
      } catch {
        // Unauthenticated visitor is a normal valid state
      } finally {
        if (isMounted) {
          setAuthReady(true);
        }
      }
    }

    initSession();

    return () => {
      isMounted = false;
    };
  }, [fetchProfile]);

  const login = async (email: string, password: string) => {
    // 1. Ensure CSRF is initialized
    await bootstrapCsrf();

    // 2. Call Django Login endpoint
    const data = await apiFetch<AuthSuccessResponse>('/auth/login/', {
      method: 'POST',
      body: JSON.stringify({ email, password }),
    });

    setAccessToken(data.access);
    setUser(data.user);
  };

  const logout = async () => {
    try {
      await apiFetch<{ message: string }>('/auth/logout/', {
        method: 'POST',
      });
    } catch {
      // Graceful error ignore on logout network failure
    } finally {
      clearSession();
      setUser(null);
    }
  };

  return (
    <AuthContext.Provider
      value={{
        user,
        authReady,
        login,
        logout,
        refreshProfile: fetchProfile,
      }}
    >
      {children}
    </AuthContext.Provider>
  );
}

export function useAuth() {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
}
