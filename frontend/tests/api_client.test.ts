import test from 'node:test';
import assert from 'node:assert';
import { getApiBaseUrl } from '../src/lib/api-client.ts';

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
