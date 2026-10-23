'use client';

import React, { useState } from 'react';
import Link from 'next/link';
import { usePathname } from 'next/navigation';
import { useAuth } from '../../context/AuthContext';
import { Home, Menu, X, ArrowRight, User, LogOut, ShieldCheck, Search } from 'lucide-react';

export default function Navbar() {
  const pathname = usePathname();
  const { user, authReady, logout } = useAuth();
  const [mobileMenuOpen, setMobileMenuOpen] = useState(false);

  const isActive = (path: string) => pathname === path;

  const navLinks = [
    { label: 'Home', href: '/' },
    { label: 'Properties', href: '/properties' },
    { label: 'Price Prediction', href: '/predict' },
    { label: 'About', href: '/about' },
    ...(user ? [{ label: 'Dashboard', href: '/dashboard' }] : []),
    ...(user?.is_staff ? [{ label: 'Admin', href: '/admin' }] : []),
  ];

  return (
    <header
      style={{
        height: 'var(--header-height)',
        backgroundColor: 'var(--color-surface)',
        borderBottom: '1px solid var(--color-border)',
        position: 'sticky',
        top: 0,
        zIndex: 50,
        display: 'flex',
        alignItems: 'center',
      }}
    >
      <div
        className="container-wide"
        style={{
          width: '100%',
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'space-between',
        }}
      >
        {/* Brand Wordmark matching Moodboard */}
        <Link
          href="/"
          style={{
            display: 'inline-flex',
            alignItems: 'center',
            gap: '10px',
            textDecoration: 'none',
          }}
        >
          <div
            className="nav-brand-logo"
            style={{
              width: '38px',
              height: '38px',
              borderRadius: 'var(--radius-sm)',
              backgroundColor: 'var(--color-primary)',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
              color: 'var(--text-on-dark)',
            }}
          >
            <Home size={20} strokeWidth={2.2} />
          </div>
          <span
            style={{
              fontFamily: 'var(--font-ui)',
              fontSize: '1.35rem',
              fontWeight: 700,
              color: 'var(--color-primary)',
              letterSpacing: '-0.03em',
            }}
          >
            GharScope
          </span>
        </Link>

        {/* Center Nav Links */}
        <nav
          style={{
            alignItems: 'center',
            gap: '36px',
          }}
          className="desktop-nav"
        >
          {navLinks.map((link) => (
            <Link
              key={link.href}
              href={link.href}
              className="nav-link-item"
              style={{
                fontWeight: isActive(link.href) ? 600 : 500,
                color: isActive(link.href) ? 'var(--color-primary)' : 'var(--text-secondary)',
              }}
            >
              {link.label}
              {isActive(link.href) && (
                <span
                  style={{
                    position: 'absolute',
                    bottom: 0,
                    left: 0,
                    right: 0,
                    height: '2px',
                    backgroundColor: 'var(--color-gold)',
                    borderRadius: '2px',
                  }}
                />
              )}
            </Link>
          ))}
        </nav>

        {/* Right Auth / Action */}
        <div
          style={{
            alignItems: 'center',
            gap: '20px',
          }}
          className="desktop-auth"
        >
          {authReady && user ? (
            <div style={{ display: 'flex', alignItems: 'center', gap: '16px' }}>
              <Link
                href="/properties"
                aria-label="Search properties"
                className="btn-icon-hover"
                style={{
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'center',
                  width: '36px',
                  height: '36px',
                  color: 'var(--color-dark)',
                  textDecoration: 'none',
                }}
              >
                <Search size={18} />
              </Link>
              <Link
                href="/dashboard"
                style={{
                  display: 'flex',
                  alignItems: 'center',
                  gap: '8px',
                  textDecoration: 'none',
                }}
              >
                <div
                  style={{
                    width: '34px',
                    height: '34px',
                    borderRadius: '50%',
                    backgroundColor: 'rgba(15, 61, 54, 0.08)',
                    display: 'flex',
                    alignItems: 'center',
                    justifyContent: 'center',
                    color: 'var(--color-primary)',
                  }}
                >
                  {user.is_staff ? <ShieldCheck size={18} /> : <User size={18} />}
                </div>
                <span style={{ fontSize: '0.875rem', fontWeight: 600, color: 'var(--color-dark)' }}>
                  {user.display_name || user.email.split('@')[0]}
                </span>
              </Link>
              <button
                onClick={() => logout()}
                className="btn-secondary"
                style={{ height: '38px', padding: '0 14px', fontSize: '0.8125rem' }}
                title="Sign Out"
              >
                <LogOut size={14} />
                <span>Sign Out</span>
              </button>
            </div>
          ) : (
            <div style={{ display: 'flex', alignItems: 'center', gap: '20px' }}>
              <Link
                href="/properties"
                aria-label="Search properties"
                className="btn-icon-hover"
                style={{
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'center',
                  width: '36px',
                  height: '36px',
                  color: 'var(--color-dark)',
                  textDecoration: 'none',
                }}
              >
                <Search size={18} />
              </Link>
              <Link
                href="/login"
                style={{
                  fontFamily: 'var(--font-ui)',
                  fontSize: '0.9375rem',
                  fontWeight: 600,
                  color: 'var(--color-dark)',
                  textDecoration: 'none',
                }}
              >
                Login
              </Link>
              <Link
                href="/predict"
                className="btn-primary"
                style={{ height: '42px', padding: '0 18px', fontSize: '0.875rem' }}
              >
                <span>Get Started</span>
                <ArrowRight size={15} />
              </Link>
            </div>
          )}
        </div>

        {/* Mobile Hamburger Toggle */}
        <button
          onClick={() => setMobileMenuOpen(!mobileMenuOpen)}
          aria-label={mobileMenuOpen ? 'Close Navigation Menu' : 'Open Navigation Menu'}
          style={{
            alignItems: 'center',
            justifyContent: 'center',
            width: '40px',
            height: '40px',
            background: 'none',
            border: 'none',
            color: 'var(--color-dark)',
            cursor: 'pointer',
          }}
          className="mobile-toggle"
        >
          {mobileMenuOpen ? <X size={24} /> : <Menu size={24} />}
        </button>
      </div>

      {/* Mobile Drawer */}
      {mobileMenuOpen && (
        <div
          style={{
            position: 'fixed',
            top: 'var(--header-height)',
            left: 0,
            right: 0,
            bottom: 0,
            backgroundColor: 'var(--color-surface)',
            borderTop: '1px solid var(--color-border)',
            padding: '28px var(--page-gutter-mobile)',
            display: 'flex',
            flexDirection: 'column',
            gap: '24px',
            zIndex: 49,
          }}
        >
          <div style={{ display: 'flex', flexDirection: 'column', gap: '16px' }}>
            {navLinks.map((link) => (
              <Link
                key={link.href}
                href={link.href}
                onClick={() => setMobileMenuOpen(false)}
                style={{
                  fontSize: '1.125rem',
                  fontWeight: 600,
                  color: isActive(link.href) ? 'var(--color-primary)' : 'var(--color-dark)',
                  padding: '8px 0',
                }}
              >
                {link.label}
              </Link>
            ))}
          </div>

          <hr style={{ border: 'none', borderTop: '1px solid var(--color-border)' }} />

          {authReady && user ? (
            <div style={{ display: 'flex', flexDirection: 'column', gap: '12px' }}>
              <div style={{ fontSize: '0.875rem', color: 'var(--text-secondary)' }}>
                Signed in as <strong>{user.email}</strong>
              </div>
              <button
                onClick={() => {
                  logout();
                  setMobileMenuOpen(false);
                }}
                className="btn-secondary"
                style={{ width: '100%' }}
              >
                <LogOut size={16} />
                <span>Sign Out</span>
              </button>
            </div>
          ) : (
            <div style={{ display: 'flex', flexDirection: 'column', gap: '12px' }}>
              <Link
                href="/login"
                onClick={() => setMobileMenuOpen(false)}
                className="btn-secondary"
                style={{ width: '100%' }}
              >
                Sign in
              </Link>
              <Link
                href="/predict"
                onClick={() => setMobileMenuOpen(false)}
                className="btn-primary"
                style={{ width: '100%' }}
              >
                <span>Get Started</span>
                <ArrowRight size={16} />
              </Link>
            </div>
          )}
        </div>
      )}

    </header>
  );
}
