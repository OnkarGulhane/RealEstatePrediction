import test from 'node:test';
import assert from 'node:assert';
import {
  getApiBaseUrl,
  getAccessToken,
  setAccessToken,
  getCsrfToken,
  setCsrfToken,
  clearSession,
  ApiClientError,
} from '../src/lib/api-client.ts';

test('getApiBaseUrl returns default URL when env var is absent', () => {
  const originalEnv = process.env.NEXT_PUBLIC_API_BASE_URL;
  delete process.env.NEXT_PUBLIC_API_BASE_URL;
  try {
    const url = getApiBaseUrl();
    assert.strictEqual(url, 'http://localhost:8000/api/v1');
  } finally {
    if (originalEnv) {
      process.env.NEXT_PUBLIC_API_BASE_URL = originalEnv;
    }
  }
});

test('getApiBaseUrl trims trailing slashes from environment URL', () => {
  const originalEnv = process.env.NEXT_PUBLIC_API_BASE_URL;
  process.env.NEXT_PUBLIC_API_BASE_URL = 'https://api.example.com/api/v1///';
  try {
    const url = getApiBaseUrl();
    assert.strictEqual(url, 'https://api.example.com/api/v1');
  } finally {
    if (originalEnv) {
      process.env.NEXT_PUBLIC_API_BASE_URL = originalEnv;
    } else {
      delete process.env.NEXT_PUBLIC_API_BASE_URL;
    }
  }
});

test('in-memory access token management is strictly ephemeral', () => {
  clearSession();
  assert.strictEqual(getAccessToken(), null);

  setAccessToken('mock_access_jwt_header.payload.sig');
  assert.strictEqual(getAccessToken(), 'mock_access_jwt_header.payload.sig');

  clearSession();
  assert.strictEqual(getAccessToken(), null);
});

test('in-memory CSRF token management preserves masked token', () => {
  clearSession();
  assert.strictEqual(getCsrfToken(), null);

  setCsrfToken('masked_csrf_token_value_abc123');
  assert.strictEqual(getCsrfToken(), 'masked_csrf_token_value_abc123');

  clearSession();
  assert.strictEqual(getCsrfToken(), null);
});

test('ApiClientError correctly captures contract error envelope details', () => {
  const err = new ApiClientError(
    400,
    'VALIDATION_ERROR',
    'Payload failed constraints',
    { area_value: ['Must be at least 100 sq.ft.'] },
    'req-uuid-1234'
  );

  assert.strictEqual(err.status, 400);
  assert.strictEqual(err.code, 'VALIDATION_ERROR');
  assert.strictEqual(err.message, 'Payload failed constraints');
  assert.deepStrictEqual(err.fields, { area_value: ['Must be at least 100 sq.ft.'] });
  assert.strictEqual(err.requestId, 'req-uuid-1234');
});
