'use client';

import React, { useState } from 'react';
import Link from 'next/link';
import { useRouter } from 'next/navigation';
import { apiFetch, ApiClientError, bootstrapCsrf } from '../../../lib/api-client';
import { Home, Eye, EyeOff, Lock, Mail, User, ArrowRight, AlertCircle } from 'lucide-react';

export default function RegisterPage() {
  const router = useRouter();

  const [displayName, setDisplayName] = useState('');
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [showPassword, setShowPassword] = useState(false);
  const [loading, setLoading] = useState(false);
  const [errorBanner, setErrorBanner] = useState<string | null>(null);
  const [fieldErrors, setFieldErrors] = useState<Record<string, string[]>>({});

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setErrorBanner(null);
    setFieldErrors({});

    if (password.length < 8) {
      setErrorBanner('Password must be at least 8 characters in length.');
      setFieldErrors({ password: ['Must be at least 8 characters.'] });
      return;
    }

    setLoading(true);
    try {
      // 1. Ensure CSRF is bootstrapped
      await bootstrapCsrf();

      // 2. Call registration endpoint
      await apiFetch<{ message: string }>('/auth/register/', {
        method: 'POST',
        body: JSON.stringify({
          email: email.trim(),
          password,
          display_name: displayName.trim() || undefined,
        }),
      });

      // 3. Redirect to login with success query param
      router.push('/login?registered=true');
    } catch (err) {
      if (err instanceof ApiClientError) {
        setErrorBanner(err.message || 'Registration failed. Please check the form.');
        if (err.fields) {
          setFieldErrors(err.fields);
        }
      } else {
        setErrorBanner('An unexpected network error occurred.');
      }
    } finally {
      setLoading(false);
    }
  };

  return (
    <div
      style={{
        minHeight: 'calc(100vh - var(--header-height) - 100px)',
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'center',
        padding: '40px var(--page-gutter-mobile)',
        backgroundColor: 'var(--bg-page)',
      }}
    >
      <div
        className="card-surface"
        style={{
          width: '100%',
          maxWidth: '440px',
          padding: '40px',
          boxShadow: 'var(--shadow-card)',
        }}
      >
        {/* Header */}
        <div style={{ textAlign: 'center', marginBottom: '28px' }}>
          <div
            style={{
              width: '44px',
              height: '44px',
              borderRadius: 'var(--radius-sm)',
              backgroundColor: 'var(--color-primary)',
              color: 'var(--text-on-dark)',
              display: 'inline-flex',
              alignItems: 'center',
              justifyContent: 'center',
              marginBottom: '16px',
            }}
          >
            <Home size={22} />
          </div>
          <h1
            className="font-display"
            style={{ fontSize: '1.75rem', fontWeight: 600, color: 'var(--color-dark)', marginBottom: '8px' }}
          >
            Create Your Account
          </h1>
          <p style={{ fontSize: '0.875rem', color: 'var(--text-secondary)' }}>
            Join GharScope to run real estate valuations and track estimates.
          </p>
        </div>

        {/* Error Banner */}
        {errorBanner && (
          <div className="alert-banner alert-error">
            <AlertCircle size={18} style={{ flexShrink: 0, marginTop: '2px' }} />
            <div>{errorBanner}</div>
          </div>
        )}

        <form onSubmit={handleSubmit}>
          {/* Display Name */}
          <div className="form-group">
            <label className="form-label" htmlFor="displayName">
              Full Name (Optional)
            </label>
            <div style={{ position: 'relative' }}>
              <input
                id="displayName"
                type="text"
                value={displayName}
                onChange={(e) => setDisplayName(e.target.value)}
                placeholder="Ramesh Sharma"
                className="form-input"
                style={{ paddingLeft: '40px' }}
              />
              <User
                size={18}
                color="var(--text-muted)"
                style={{ position: 'absolute', left: '12px', top: '50%', transform: 'translateY(-50%)' }}
              />
            </div>
            {fieldErrors['display_name'] && (
              <span className="field-error">{fieldErrors['display_name'].join(' ')}</span>
            )}
          </div>

          {/* Email */}
          <div className="form-group">
            <label className="form-label" htmlFor="email">
              Email Address
            </label>
            <div style={{ position: 'relative' }}>
              <input
                id="email"
                type="email"
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                placeholder="buyer@example.com"
                required
                className="form-input"
                style={{ paddingLeft: '40px' }}
              />
              <Mail
                size={18}
                color="var(--text-muted)"
                style={{ position: 'absolute', left: '12px', top: '50%', transform: 'translateY(-50%)' }}
              />
            </div>
            {fieldErrors['email'] && (
              <span className="field-error">{fieldErrors['email'].join(' ')}</span>
            )}
          </div>

          {/* Password */}
          <div className="form-group" style={{ marginBottom: '24px' }}>
            <label className="form-label" htmlFor="password">
              Password (Minimum 8 Characters)
            </label>
            <div style={{ position: 'relative' }}>
              <input
                id="password"
                type={showPassword ? 'text' : 'password'}
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                placeholder="••••••••"
                required
                minLength={8}
                className="form-input"
                style={{ paddingLeft: '40px', paddingRight: '40px' }}
              />
              <Lock
                size={18}
                color="var(--text-muted)"
                style={{ position: 'absolute', left: '12px', top: '50%', transform: 'translateY(-50%)' }}
              />
              <button
                type="button"
                onClick={() => setShowPassword(!showPassword)}
                style={{
                  position: 'absolute',
                  right: '12px',
                  top: '50%',
                  transform: 'translateY(-50%)',
                  background: 'none',
                  border: 'none',
                  cursor: 'pointer',
                  color: 'var(--text-muted)',
                  display: 'flex',
                  alignItems: 'center',
                }}
                aria-label={showPassword ? 'Hide password' : 'Show password'}
              >
                {showPassword ? <EyeOff size={18} /> : <Eye size={18} />}
              </button>
            </div>
            {fieldErrors['password'] && (
              <span className="field-error">{fieldErrors['password'].join(' ')}</span>
            )}
          </div>

          {/* Submit */}
          <button
            type="submit"
            disabled={loading}
            className="btn-primary"
            style={{ width: '100%', height: '48px', fontSize: '1rem' }}
          >
            <span>{loading ? 'Creating Account...' : 'Register Account'}</span>
            {!loading && <ArrowRight size={18} />}
          </button>
        </form>

        <div style={{ textAlign: 'center', marginTop: '24px', fontSize: '0.875rem', color: 'var(--text-secondary)' }}>
          Already have an account?{' '}
          <Link href="/login" style={{ color: 'var(--color-primary)', fontWeight: 600, textDecoration: 'underline' }}>
            Sign In here
          </Link>
        </div>
      </div>
    </div>
  );
}
