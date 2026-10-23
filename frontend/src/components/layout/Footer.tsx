import React from 'react';
import Link from 'next/link';
import { Home, ShieldCheck, MapPin, Database } from 'lucide-react';

export default function Footer() {
  return (
    <footer
      style={{
        backgroundColor: 'var(--color-primary-dark)',
        color: 'var(--color-surface)',
        paddingTop: '64px',
        paddingBottom: '40px',
        borderTop: '1px solid rgba(216, 210, 196, 0.15)',
      }}
    >
      <div className="container-wide">
        {/* Main Grid */}
        <div
          style={{
            display: 'grid',
            gridTemplateColumns: 'repeat(auto-fit, minmax(240px, 1fr))',
            gap: '40px',
            marginBottom: '48px',
          }}
        >
          {/* Brand Info */}
          <div style={{ maxWidth: '360px' }}>
            <div style={{ display: 'flex', alignItems: 'center', gap: '10px', marginBottom: '16px' }}>
              <div
                style={{
                  width: '32px',
                  height: '32px',
                  borderRadius: 'var(--radius-sm)',
                  backgroundColor: 'var(--color-primary)',
                  border: '1px solid var(--color-sage)',
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'center',
                  color: 'var(--color-surface)',
                }}
              >
                <Home size={18} />
              </div>
              <span
                style={{
                  fontFamily: 'var(--font-ui)',
                  fontSize: '1.25rem',
                  fontWeight: 700,
                  letterSpacing: '-0.02em',
                  color: 'var(--color-surface)',
                }}
              >
                GharScope
              </span>
            </div>
            <p
              style={{
                fontFamily: 'var(--font-display)',
                fontStyle: 'italic',
                fontSize: '1.0625rem',
                color: 'var(--color-gold)',
                marginBottom: '12px',
              }}
            >
              Know the Value. Find Your Place.
            </p>
            <p style={{ fontSize: '0.875rem', color: '#A3B3AB', lineHeight: 1.6 }}>
              Statistical residential real estate valuation engine powered by verified machine learning across 81 Indian micro-markets.
            </p>
          </div>

          {/* Quick Links */}
          <div>
            <h4
              style={{
                fontSize: '0.875rem',
                fontWeight: 700,
                letterSpacing: '0.08em',
                textTransform: 'uppercase',
                color: 'var(--color-gold)',
                marginBottom: '16px',
              }}
            >
              Platform
            </h4>
            <ul style={{ listStyle: 'none', display: 'flex', flexDirection: 'column', gap: '12px', padding: 0, margin: 0 }}>
              <li>
                <Link href="/properties" style={{ fontSize: '0.9375rem', color: '#D4DDD8', textDecoration: 'none' }}>
                  Property Catalogue
                </Link>
              </li>
              <li>
                <Link href="/predict" style={{ fontSize: '0.9375rem', color: '#D4DDD8', textDecoration: 'none' }}>
                  Price Prediction
                </Link>
              </li>
              <li>
                <Link href="/about" style={{ fontSize: '0.9375rem', color: '#D4DDD8', textDecoration: 'none' }}>
                  Methodology & Limitations
                </Link>
              </li>
              <li>
                <Link href="/dashboard" style={{ fontSize: '0.9375rem', color: '#D4DDD8', textDecoration: 'none' }}>
                  User Dashboard
                </Link>
              </li>
              <li>
                <Link href="/login" style={{ fontSize: '0.9375rem', color: '#D4DDD8', textDecoration: 'none' }}>
                  Login / Account
                </Link>
              </li>
            </ul>
          </div>

          {/* Offline Validation Proof */}
          <div>
            <h4
              style={{
                fontSize: '0.875rem',
                fontWeight: 700,
                letterSpacing: '0.08em',
                textTransform: 'uppercase',
                color: 'var(--color-gold)',
                marginBottom: '16px',
              }}
            >
              Model Evaluation
            </h4>
            <div style={{ display: 'flex', flexDirection: 'column', gap: '10px' }}>
              <div style={{ display: 'flex', alignItems: 'center', gap: '8px', fontSize: '0.875rem', color: '#D4DDD8' }}>
                <MapPin size={16} color="var(--color-gold)" />
                <span>81 Indian Micro-Markets</span>
              </div>
              <div style={{ display: 'flex', alignItems: 'center', gap: '8px', fontSize: '0.875rem', color: '#D4DDD8' }}>
                <Database size={16} color="var(--color-gold)" />
                <span>Holdout R²: 0.7104 (HistGradient)</span>
              </div>
              <div style={{ display: 'flex', alignItems: 'center', gap: '8px', fontSize: '0.875rem', color: '#D4DDD8' }}>
                <ShieldCheck size={16} color="var(--color-gold)" />
                <span>MAE ₹26.94L (Offline Test)</span>
              </div>
            </div>
          </div>
        </div>

        {/* Legal Disclaimer Box */}
        <div
          style={{
            borderTop: '1px solid rgba(255, 255, 255, 0.1)',
            paddingTop: '24px',
            marginBottom: '24px',
            fontSize: '0.75rem',
            color: '#8A9A92',
            lineHeight: 1.6,
          }}
        >
          <strong style={{ color: 'var(--color-gold)' }}>Honest Disclosure: </strong>
          GharScope provides statistical property estimates derived from historical market listings and machine learning algorithms. Estimates serve as indicative market research tools and are not official certified architectural appraisals, municipal valuation certificates, or guaranteed transaction amounts.
        </div>

        {/* Bottom Bar */}
        <div
          style={{
            display: 'flex',
            flexWrap: 'wrap',
            justifyContent: 'space-between',
            alignItems: 'center',
            fontSize: '0.8125rem',
            color: '#8A9A92',
            gap: '12px',
          }}
        >
          <span>© 2026 GharScope. All rights reserved.</span>
          <span>India Real Estate Valuation Platform</span>
        </div>
      </div>
    </footer>
  );
}
