/**
 * GharScope Typed API Client
 * - Exclusively communicates with Django REST Framework (http://localhost:8000/api/v1).
 * - Never calls FastAPI directly from browser.
 * - Access JWT held strictly in memory.
 * - Refresh token held in HttpOnly cookie.
 * - Handles CSRF bootstrap & injection.
 * - Single-flight refresh token queue preventing duplicate refresh requests.
 * - Parses contract-compliant error envelope: { error: { code, message, fields, request_id } }.
 */

import type { ApiErrorEnvelope, TokenRefreshResponse } from '../types';

let inMemoryAccessToken: string | null = null;
let inMemoryCsrfToken: string | null = null;
let refreshPromise: Promise<string | null> | null = null;

export function getAccessToken(): string | null {
  return inMemoryAccessToken;
}

export function setAccessToken(token: string | null): void {
  inMemoryAccessToken = token;
}

export function getCsrfToken(): string | null {
  return inMemoryCsrfToken;
}

export function setCsrfToken(token: string | null): void {
  inMemoryCsrfToken = token;
}

export function clearSession(): void {
  inMemoryAccessToken = null;
  inMemoryCsrfToken = null;
  refreshPromise = null;
}

export function getApiBaseUrl(): string {
  const envUrl = process.env.NEXT_PUBLIC_API_BASE_URL;
  if (!envUrl) {
    return 'http://localhost:8000/api/v1';
  }
  return envUrl.replace(/\/+$/, '');
}

export class ApiClientError extends Error {
  public status: number;
  public code: string;
  public fields?: Record<string, string[]>;
  public requestId?: string;

  constructor(
    status: number,
    code: string,
    message: string,
    fields?: Record<string, string[]>,
    requestId?: string
  ) {
    super(message);
    this.name = 'ApiClientError';
    this.status = status;
    this.code = code;
    this.fields = fields;
    this.requestId = requestId;
  }
}

/**
 * Bootstrap CSRF token and cookie from Django
 */
export async function bootstrapCsrf(): Promise<string | null> {
  try {
    const baseUrl = getApiBaseUrl();
    const res = await fetch(`${baseUrl}/auth/csrf/`, {
      method: 'GET',
      credentials: 'include',
      headers: {
        Accept: 'application/json',
      },
    });

    if (res.ok) {
      const data = await res.json() as { csrf_token: string };
      setCsrfToken(data.csrf_token);
      return data.csrf_token;
    }
  } catch {
    // Graceful fallback on network error
  }
  return null;
}

/**
 * Single-flight token refresh to avoid concurrent race conditions
 */
export async function refreshAccessToken(): Promise<string | null> {
  if (refreshPromise) {
    return refreshPromise;
  }

  refreshPromise = (async () => {
    try {
      const baseUrl = getApiBaseUrl();
      const headers: Record<string, string> = {
        'Content-Type': 'application/json',
        Accept: 'application/json',
      };

      if (inMemoryCsrfToken) {
        headers['X-CSRFToken'] = inMemoryCsrfToken;
      }

      const res = await fetch(`${baseUrl}/auth/refresh/`, {
        method: 'POST',
        credentials: 'include',
        headers,
      });

      if (!res.ok) {
        clearSession();
        return null;
      }

      const data = await res.json() as TokenRefreshResponse;
      setAccessToken(data.access);
      return data.access;
    } catch {
      clearSession();
      return null;
    } finally {
      refreshPromise = null;
    }
  })();

  return refreshPromise;
}

/**
 * Main authenticated API fetch wrapper
 */
export async function apiFetch<T>(
  endpoint: string,
  options: RequestInit = {},
  isRetry = false
): Promise<T> {
  const baseUrl = getApiBaseUrl();
  const normalizedEndpoint = endpoint.startsWith('/') ? endpoint : `/${endpoint}`;
  const targetUrl = `${baseUrl}${normalizedEndpoint}`;

  const headers: Record<string, string> = {
    'Content-Type': 'application/json',
    Accept: 'application/json',
    ...(options.headers as Record<string, string> || {}),
  };

  if (inMemoryAccessToken && !headers['Authorization']) {
    headers['Authorization'] = `Bearer ${inMemoryAccessToken}`;
  }

  const method = (options.method || 'GET').toUpperCase();
  if (inMemoryCsrfToken && method !== 'GET' && method !== 'HEAD' && !headers['X-CSRFToken']) {
    headers['X-CSRFToken'] = inMemoryCsrfToken;
  }

  let response: Response;
  try {
    response = await fetch(targetUrl, {
      ...options,
      credentials: 'include',
      headers,
    });
  } catch (err) {
    throw new ApiClientError(
      0,
      'NETWORK_ERROR',
      err instanceof Error ? err.message : 'Network connection failure. Please check your internet connection.'
    );
  }

  // Handle 401 Unauthorized with single-flight refresh & at most 1 retry
  const isAuthEndpoint = normalizedEndpoint.startsWith('/auth/login') ||
                         normalizedEndpoint.startsWith('/auth/refresh') ||
                         normalizedEndpoint.startsWith('/auth/csrf');

  if (response.status === 401 && !isRetry && !isAuthEndpoint) {
    const newAccess = await refreshAccessToken();
    if (newAccess) {
      return apiFetch<T>(endpoint, options, true);
    }
  }

  if (!response.ok) {
    let errorCode = 'API_ERROR';
    let errorMessage = `Server error (${response.status})`;
    let fieldErrors: Record<string, string[]> | undefined;
    let requestId: string | undefined;

    try {
      const errorJson = await response.json() as ApiErrorEnvelope;
      if (errorJson?.error) {
        errorCode = errorJson.error.code || errorCode;
        errorMessage = errorJson.error.message || errorMessage;
        fieldErrors = errorJson.error.fields;
        requestId = errorJson.error.request_id;
      }
    } catch {
      // Non-JSON response
    }

    throw new ApiClientError(response.status, errorCode, errorMessage, fieldErrors, requestId);
  }

  // 204 No Content
  if (response.status === 204) {
    return {} as T;
  }

  return response.json() as Promise<T>;
}

/**
 * Backward-compatible fetch function preserving original tests
 */
export async function fetchFromBackend<T>(endpoint: string, options: RequestInit = {}): Promise<T> {
  return apiFetch<T>(endpoint, options);
}
